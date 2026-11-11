"""Genera tabla ejecutiva de entidades geopolíticas con great_tables"""

import logging
from pathlib import Path

import pandas as pd
from great_tables import GT

try:
    from src.data_loader import load_json
    from src.validator import validate_entities
except ImportError:  # ejecución directa: python src/generate_tables.py
    from data_loader import load_json
    from validator import validate_entities

logger = logging.getLogger(__name__)


def generate() -> None:
    ner_file = Path("data/export/ner_entities.json")
    if not ner_file.exists():
        logger.warning(
            "ner_entities.json no encontrado, ejecutar ner_analysis.py primero"
        )
        return

    data = load_json(ner_file)
    entities = validate_entities(data["top_entities"][:10])
    df = pd.DataFrame(entities)[["entity", "label", "count"]]
    df.columns = ["Entidad", "Tipo", "Frecuencia"]

    tbl = (
        GT(df)
        .tab_header(title="Top 10 Entidades Geopolíticas, Discursos Patronato")
        .tab_source_note("Fuente: NER spaCy es_core_news_sm | Análisis: Álvaro Salinas")
    )
    Path("assets").mkdir(exist_ok=True)
    tbl.save("assets/executive_table.html")
    logger.info("assets/executive_table.html generado")


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    generate()
