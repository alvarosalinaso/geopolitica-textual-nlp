"""Topic analysis: bigrams + LDA for Chilean presidential speeches."""

import json
import math
import re
from pathlib import Path

import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

BASE = Path(__file__).parent.parent

# Cache for the spaCy lemmatization model (loaded once if lemmatize=True).
_NLP_LEMMA = None


def _get_nlp_lemma():
    global _NLP_LEMMA
    if _NLP_LEMMA is None and SPACY_AVAILABLE:
        try:
            _NLP_LEMMA = spacy.load("es_core_news_sm", disable=["ner", "parser"])
        except OSError:
            pass
    return _NLP_LEMMA


def _clean(text, lemmatize=False):
    """Normaliza texto: minúsculas, sin puntuación, sin stopwords.

    Si lemmatize=True y spaCy + es_core_news_sm están disponibles, aplica
    lematización (opcional; por defecto off para no requerir el modelo).
    Nota: "han sido", "ha sido", "ha de" se quitaron de la lista de stopwords:
    eran entradas mult palabra que nunca podían coincidir al filtrar por token.
    """
    text = text.lower()
    text = re.sub(r"[^a-záéíóúñü\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if lemmatize:
        nlp = _get_nlp_lemma()
        if nlp is not None:
            doc = nlp(text)
            text = " ".join(token.lemma_ for token in doc)

    stopwords = {
        "de",
        "la",
        "el",
        "en",
        "y",
        "a",
        "que",
        "es",
        "se",
        "del",
        "los",
        "las",
        "un",
        "una",
        "por",
        "con",
        "no",
        "para",
        "al",
        "lo",
        "como",
        "su",
        "más",
        "este",
        "ha",
        "han",
        "fue",
        "ser",
        "sobre",
        "todo",
        "entre",
        "desde",
        "sin",
        "pero",
        "muy",
        "ya",
        "o",
        "e",
        "ni",
        "le",
        "les",
        "da",
        "dos",
        "cada",
        "uno",
        "otra",
        "otro",
        "otros",
        "otras",
    }
    words = [w for w in text.split() if w not in stopwords and len(w) > 2]
    return " ".join(words)


def _umass_coherence(topics_words, word_matrix, feature_names):
    """Coherencia UMass para una lista de topics.

    Para cada topic, suma log((D(w_i ∩ w_j) + ε) / (D(w_j) + ε)) sobre los
    pares (i > j) de sus top-10 palabras, donde D(·) es el número de
    documentos que contienen la palabra. Implementación local, sin gensim.

    Returns:
        Lista de scores de coherencia (uno por topic) y el promedio.
    """
    word_to_idx = {name: i for i, name in enumerate(feature_names)}

    # Presencia binaria por documento (matriz dispersa booleana).
    presence = word_matrix.copy()
    presence.data = (presence.data > 0).astype(int)

    epsilon = 1e-10
    coherence_scores = []
    for topic in topics_words:
        top_words = topic["words"][:10]
        if len(top_words) < 2:
            coherence_scores.append(0.0)
            continue
        score_sum = 0.0
        n_pairs = 0
        for i in range(1, len(top_words)):
            for j in range(i):
                idx_i = word_to_idx.get(top_words[i])
                idx_j = word_to_idx.get(top_words[j])
                if idx_i is None or idx_j is None:
                    continue
                col_i = presence[:, idx_i].toarray().ravel()
                col_j = presence[:, idx_j].toarray().ravel()
                d_j = int(col_j.sum())
                d_ij = int(((col_i > 0) & (col_j > 0)).sum())
                score_sum += math.log((d_ij + epsilon) / (d_j + epsilon))
                n_pairs += 1
        coherence_scores.append(score_sum / n_pairs if n_pairs > 0 else 0.0)

    avg = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0
    return coherence_scores, avg


def analyze_topics(n_topics=5):
    csv_path = BASE / "data" / "processed" / "speeches.csv"
    if not csv_path.exists():
        return None

    df = pd.read_csv(csv_path)
    df["clean_text"] = df["text"].apply(_clean)

    vectorizer = CountVectorizer(min_df=2, max_features=200, ngram_range=(2, 2))
    try:
        bigram_matrix = vectorizer.fit_transform(df["clean_text"])
    except ValueError:
        bigram_matrix = None
        bigram_names = []

    bigrams = []
    if bigram_matrix is not None:
        bigram_names = vectorizer.get_feature_names_out()
        bigram_counts = bigram_matrix.sum(axis=0).A1
        bigram_pairs = sorted(zip(bigram_names, bigram_counts), key=lambda x: -x[1])
        bigrams = [{"bigram": b, "count": int(c)} for b, c in bigram_pairs[:30]]

    vectorizer_words = CountVectorizer(min_df=1, max_features=500)
    word_matrix = vectorizer_words.fit_transform(df["clean_text"])

    feature_names = vectorizer_words.get_feature_names_out()

    # Try multiple k values and pick the one with highest UMass coherence
    best_k = n_topics
    best_coherence = -float("inf")
    best_result = None
    k_candidates = [n_topics, n_topics + 1, n_topics + 2, n_topics + 3, n_topics + 4]

    for candidate_k in k_candidates:
        lda_temp = LatentDirichletAllocation(
            n_components=candidate_k, random_state=42, max_iter=50
        )
        doc_topics_temp = lda_temp.fit_transform(word_matrix)

        topics_temp = []
        for idx, topic in enumerate(lda_temp.components_):
            top_words = [feature_names[i] for i in topic.argsort()[-10:][::-1]]
            topics_temp.append(
                {
                    "topic_id": idx,
                    "words": top_words,
                    "weight": round(float(topic.sum()), 2),
                }
            )

        _coherence_scores, avg_coherence = _umass_coherence(
            topics_temp, word_matrix, feature_names
        )

        if avg_coherence > best_coherence:
            best_coherence = avg_coherence
            best_k = candidate_k
            best_result = {
                "total_documents": len(df),
                "total_bigrams": len(bigrams),
                "bigrams": bigrams,
                "topics": topics_temp,
                "document_topics": [
                    {
                        "year": int(row["year"]),
                        "speaker": row["speaker"],
                        "topic": int(doc_topics_temp[i].argmax()),
                        "weight": round(float(doc_topics_temp[i].max()), 3),
                    }
                    for i, row in df.iterrows()
                ],
            }

    if best_result is None:
        return None

    result = best_result
    result["coherence_umass"] = round(best_coherence, 4)
    result["best_k"] = best_k
    result["k_candidates"] = k_candidates
    result["coherence_method"] = "umass_local"

    output = BASE / "data" / "export" / "topics.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


if __name__ == "__main__":
    result = analyze_topics()
    if result:
        print(f"Documents: {result['total_documents']}")
        print(f"Bigrams found: {result['total_bigrams']}")
        print(f"Topics (k={result['best_k']}): {len(result['topics'])}")
        print(f"UMass coherence: {result['coherence_umass']}")
        for t in result["topics"]:
            print(f"  Topic {t['topic_id']}: {', '.join(t['words'][:5])}")
    else:
        print("No data found")
