"""
Cifras clave reproducibles para el README.

Computa menciones GPE/LOC sobre el corpus real BCN
(data/processed/speeches.csv) con spaCy es_core_news_sm, y guarda el
resultado en data/export/key_figures.json. El README cita estas cifras
con la fecha de corrida; no hay números precalculados en el repo.

Uso:
    python src/key_figures.py
"""

from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path

try:
    import spacy

    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

try:
    from src.data_loader import PROJECT_ROOT, load_speeches, write_json
    from src.metrics import percentage
except ImportError:  # ejecución directa: python src/key_figures.py
    from data_loader import PROJECT_ROOT, load_speeches, write_json
    from metrics import percentage

logger = logging.getLogger(__name__)

BASE = PROJECT_ROOT
GPE_LOC = ("GPE", "LOC")


def compute_key_figures(csv_path: Path | None = None) -> dict:
    """Extrae menciones GPE/LOC y devuelve cifras agregadas."""
    if not DEPS_AVAILABLE:
        raise RuntimeError("Se requieren pandas y spacy")

    if csv_path is None:
        csv_path = BASE / "data" / "processed" / "speeches.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} no existe. Ejecuta primero: python src/collect_speeches.py"
        )

    df = load_speeches(csv_path)
    nlp = spacy.load("es_core_news_sm", disable=["parser", "lemmatizer"])

    counter: Counter[str] = Counter()
    for text in df["text"].astype(str):
        doc = nlp(text[:150000])
        for ent in doc.ents:
            if ent.label_ in GPE_LOC:
                name = ent.text.strip()
                if name:
                    counter[name] += 1

    total = sum(counter.values())
    santiago_aliases = ("Santiago", "Santiago de Chile")
    santiago = sum(counter[a] for a in santiago_aliases if a in counter)

    top = counter.most_common(15)
    figures = {
        "corpus": str(csv_path.relative_to(BASE))
        if csv_path.is_relative_to(BASE)
        else str(csv_path),
        "n_speeches": len(df),
        "year_min": int(df["year"].min()),
        "year_max": int(df["year"].max()),
        "model": "es_core_news_sm",
        "total_gpe_loc_mentions": total,
        "unique_places": len(counter),
        "santiago_mentions": santiago,
        "santiago_share_pct": percentage(santiago, total),
        "top_places": [{"place": p, "mentions": c} for p, c in top],
    }
    return figures


def main() -> None:
    figures = compute_key_figures()
    out = write_json(figures, BASE / "data" / "export" / "key_figures.json")

    logger.info(
        "Corpus: %d discursos (%d-%d)",
        figures["n_speeches"],
        figures["year_min"],
        figures["year_max"],
    )
    logger.info(
        "Menciones GPE/LOC: %d (%d lugares únicos)",
        figures["total_gpe_loc_mentions"],
        figures["unique_places"],
    )
    logger.info(
        "Santiago: %d menciones (%s%%)",
        figures["santiago_mentions"],
        figures["santiago_share_pct"],
    )
    for row in figures["top_places"][:5]:
        logger.info("Top: %s = %d", row["place"], row["mentions"])
    logger.info("Guardado en %s", out)


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    main()
