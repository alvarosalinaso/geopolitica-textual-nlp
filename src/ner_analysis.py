"""
Named Entity Recognition (NER) para análisis geopolítico.
Extrae entidades geopolíticas de discursos del Patronato using spaCy.
"""

from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path

try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import pandas as pd  # noqa: F401

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from src.data_loader import find_corpus, list_text_files, load_speeches, write_json
except ImportError:  # ejecución directa: python src/ner_analysis.py
    from data_loader import find_corpus, list_text_files, load_speeches, write_json

logger = logging.getLogger(__name__)

ENTITY_LABELS: tuple[str, ...] = ("LOC", "GPE", "ORG", "PERSON", "NORP")
MAX_CHARS = 100_000


def run_ner_analysis(
    data_dir: Path = Path("data"), output_dir: Path = Path("data/export")
) -> dict:
    """
    Extrae entidades geopolíticas usando spaCy NER.

    Returns:
        dict con estadísticas de entidades encontradas
    """
    if not SPACY_AVAILABLE:
        logger.warning(
            "spaCy no instalado. Saltando NER. "
            "pip install spacy && python -m spacy download es_core_news_sm"
        )
        return {}

    try:
        nlp = spacy.load("es_core_news_sm")
    except OSError:
        logger.warning(
            "Modelo es_core_news_sm no encontrado. "
            "Ejecuta: python -m spacy download es_core_news_sm"
        )
        return {}

    all_entities: list[dict[str, str]] = []

    def _collect(text: str, source: str) -> None:
        doc = nlp(text[:MAX_CHARS])
        for ent in doc.ents:
            if ent.label_ in ENTITY_LABELS:
                all_entities.append(
                    {
                        "text": ent.text.strip(),
                        "label": ent.label_,
                        "source_file": source,
                    }
                )

    corpus_path = find_corpus(data_dir)
    if PANDAS_AVAILABLE and corpus_path is not None:
        df = load_speeches(corpus_path)
        for _, row in df.iterrows():
            source = f"{row['speaker']} {row['year']}".strip()
            _collect(str(row["text"]), source)

    text_files = list_text_files(data_dir)
    for tf in text_files:
        _collect(tf.read_text(encoding="utf-8", errors="ignore"), tf.name)

    entity_counts = Counter((e["text"], e["label"]) for e in all_entities)
    label_totals = dict(Counter(e["label"] for e in all_entities))

    top_entities = [
        {"entity": text, "label": label, "count": count}
        for (text, label), count in entity_counts.most_common(30)
    ]

    write_json(
        {
            "total_entities": len(all_entities),
            "label_totals": label_totals,
            "top_entities": top_entities,
        },
        output_dir / "ner_entities.json",
    )

    logger.info(
        "%d entidades extraídas (corpus + %d archivos de texto)",
        len(all_entities),
        len(text_files),
    )
    logger.info("Top 5: %s", [e["entity"] for e in top_entities[:5]])

    return {"total": len(all_entities), "top": top_entities[:10]}


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    run_ner_analysis()
