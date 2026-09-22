"""Topic analysis: bigrams + LDA for Chilean presidential speeches."""

import json
import re
from pathlib import Path

import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

BASE = Path(__file__).parent.parent


def _clean(text):
    text = text.lower()
    text = re.sub(r"[^a-záéíóúñü\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    stopwords = [
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
        "han sido",
        "ha sido",
        "fue",
        "ser",
        "ha de",
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
    ]
    words = [w for w in text.split() if w not in stopwords and len(w) > 2]
    return " ".join(words)


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

    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=50)
    doc_topics = lda.fit_transform(word_matrix)

    feature_names = vectorizer_words.get_feature_names_out()
    topics = []
    for idx, topic in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic.argsort()[-10:][::-1]]
        topics.append(
            {
                "topic_id": idx,
                "words": top_words,
                "weight": round(float(topic.sum()), 2),
            }
        )

    doc_topic_list = []
    for i, row in df.iterrows():
        dominant = int(doc_topics[i].argmax())
        doc_topic_list.append(
            {
                "year": int(row["year"]),
                "speaker": row["speaker"],
                "topic": dominant,
                "weight": round(float(doc_topics[i][dominant]), 3),
            }
        )

    result = {
        "total_documents": len(df),
        "total_bigrams": len(bigrams),
        "bigrams": bigrams,
        "topics": topics,
        "document_topics": doc_topic_list,
    }

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
        print(f"Topics: {len(result['topics'])}")
        for t in result["topics"]:
            print(f"  Topic {t['topic_id']}: {', '.join(t['words'][:5])}")
    else:
        print("No data found")
