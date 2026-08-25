"""Genera tabla ejecutiva de entidades geopolíticas con great_tables"""

import json
from pathlib import Path

import pandas as pd
from great_tables import GT


def generate():
    ner_file = Path("data/export/ner_entities.json")
    if not ner_file.exists():
        print(
            "[TABLE] ner_entities.json no encontrado — ejecutar ner_analysis.py primero"
        )
        return

    with open(ner_file, encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data["top_entities"][:10])
    df.columns = ["Entidad", "Tipo", "Frecuencia"]

    tbl = (
        GT(df)
        .tab_header(title="Top 10 Entidades Geopolíticas — Discursos Patronato")
        .tab_source_note("Fuente: NER spaCy es_core_news_sm | Análisis: Álvaro Salinas")
    )
    Path("assets").mkdir(exist_ok=True)
    tbl.save("assets/executive_table.html")
    print("[TABLE] assets/executive_table.html generado")


if __name__ == "__main__":
    generate()
