"""
Named Entity Recognition (NER) para análisis geopolítico.
Extrae entidades geopolíticas de discursos del Patronato using spaCy.
"""
import json
from collections import Counter
from pathlib import Path

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def run_ner_analysis(data_dir: Path = Path("data"), output_dir: Path = Path("data/export")) -> dict:
    """
    Extrae entidades geopolíticas usando spaCy NER.

    Returns:
        dict con estadísticas de entidades encontradas
    """
    if not SPACY_AVAILABLE:
        print("[NER] spaCy no instalado. Saltando NER. pip install spacy && python -m spacy download es_core_news_sm")
        return {}

    try:
        nlp = spacy.load("es_core_news_sm")
    except OSError:
        print("[NER] Modelo es_core_news_sm no encontrado. Ejecuta: python -m spacy download es_core_news_sm")
        return {}

    all_entities = []

    csv_path = data_dir / "processed" / "speeches.csv"
    fallback_csv = data_dir / "sample_speeches.csv"
    if PANDAS_AVAILABLE and csv_path.exists():
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            text = str(row.get("text", ""))
            source = str(row.get("speaker", "")) + " " + str(row.get("year", ""))
            doc = nlp(text[:100000])
            for ent in doc.ents:
                if ent.label_ in ("LOC", "GPE", "ORG", "PERSON", "NORP"):
                    all_entities.append({
                        "text": ent.text.strip(),
                        "label": ent.label_,
                        "source_file": source.strip(),
                    })
    elif PANDAS_AVAILABLE and fallback_csv.exists():
        df = pd.read_csv(fallback_csv)
        for _, row in df.iterrows():
            text = str(row.get("text", ""))
            source = str(row.get("speaker", "")) + " " + str(row.get("year", ""))
            doc = nlp(text[:100000])
            for ent in doc.ents:
                if ent.label_ in ("LOC", "GPE", "ORG", "PERSON", "NORP"):
                    all_entities.append({
                        "text": ent.text.strip(),
                        "label": ent.label_,
                        "source_file": source.strip(),
                    })

    text_files = list(data_dir.rglob("*.txt")) + list(data_dir.rglob("*.md"))
    for tf in text_files:
        text = tf.read_text(encoding="utf-8", errors="ignore")
        doc = nlp(text[:100000])

        for ent in doc.ents:
            if ent.label_ in ("LOC", "GPE", "ORG", "PERSON", "NORP"):
                all_entities.append({
                    "text": ent.text.strip(),
                    "label": ent.label_,
                    "source_file": tf.name,
                })

    entity_counts = Counter((e["text"], e["label"]) for e in all_entities)

    top_entities = [
        {"entity": text, "label": label, "count": count}
        for (text, label), count in entity_counts.most_common(30)
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "ner_entities.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"total_entities": len(all_entities), "top_entities": top_entities}, f, ensure_ascii=False, indent=2)

    print(f"[NER] {len(all_entities)} entidades extraídas de {len(text_files)} archivos")
    print(f"[NER] Top 5: {[e['entity'] for e in top_entities[:5]]}")

    return {"total": len(all_entities), "top": top_entities[:10]}


if __name__ == "__main__":
    run_ner_analysis()
