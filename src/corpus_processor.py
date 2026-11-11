from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd
import spacy

try:
    from src.data_loader import find_corpus, read_table
    from src.validator import (
        REQUIRED_SPEECH_COLUMNS,
        validate_columns,
        validate_speeches,
    )
except ImportError:  # ejecución directa: python src/corpus_processor.py
    from data_loader import find_corpus, read_table
    from validator import (
        REQUIRED_SPEECH_COLUMNS,
        validate_columns,
        validate_speeches,
    )

logger = logging.getLogger(__name__)

# Notas de despliegue: Si es primera vez, se debe instalar el modelo de spacy localmente con:
# python -m spacy download es_core_news_sm
# python -m spacy download es_core_news_md  # optional, for vector similarity


class GeopoliticalExtractor:
    """
    Motor NLP basado en Arquitectura de Extracción de Entidades (NER).
    Analiza un corpus buscando explícitamente entidades del tipo GPE (Geo-Political Entity)
    y LOC (Locations).
    """

    def __init__(self, model_size: str = "es_core_news_sm"):
        # Modelo pequeño (Small) por defecto para despliegue ligero y rápido.
        # El modelo mediano (md) tiene vectores pero es más pesado.
        try:
            self.nlp = spacy.load(model_size)
        except OSError:
            logger.warning(
                "Modelo spaCy '%s' no disponible. Ejecuta: python -m spacy download %s",
                model_size,
                model_size,
            )
            self.nlp = None

    def process_corpus(self, csv_filepath: Path | str) -> pd.DataFrame:
        """
        Recibe un CSV con discursos históricos y extrae sus menciones espaciales.
        Retorna un DataFrame enriquecido listo para georeferenciación.
        """
        if not self.nlp:
            return pd.DataFrame()

        name = Path(csv_filepath).name
        df = validate_columns(read_table(csv_filepath), REQUIRED_SPEECH_COLUMNS, name)
        if df.empty:
            logger.warning("%s no tiene filas; no hay entidades que extraer", name)
            return pd.DataFrame()
        df = validate_speeches(df, name=name)
        extracted_data = []

        for _, row in df.iterrows():
            text = row["text"]
            doc = self.nlp(text)

            # Filtramos solo Entidades Geopolíticas mencionadas por el orador
            places = [ent.text for ent in doc.ents if ent.label_ in ["LOC", "GPE"]]

            for place in places:
                extracted_data.append(
                    {
                        "Year": row["year"],
                        "Speaker": row["speaker"],
                        "Mentioned_Location": place,
                    }
                )

        return pd.DataFrame(extracted_data)

    def extract_entities(self, text: str) -> list[dict[str, Any]]:
        """
        Extrae entidades con sus posiciones en el texto (start/end) y etiqueta.

        Nota: los modelos en español de spaCy no exponen un score de confianza
        por entidad; no se fabrica ninguno.
        """
        if not self.nlp:
            return []

        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            if ent.label_ in ["LOC", "GPE", "ORG", "PERSON", "NORP"]:
                entities.append(
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start_char": ent.start_char,
                        "end_char": ent.end_char,
                    }
                )

        return entities


def create_sample_speeches() -> pd.DataFrame:
    """Create sample speeches for testing/demo purposes."""
    return pd.DataFrame(
        {
            "year": [1881, 1885, 1910, 1925, 1960, 1990, 2010],
            "speaker": [
                "Presidente A",
                "Presidente B",
                "Presidente C",
                "Presidente D",
                "Presidente E",
                "Presidente F",
                "Presidente G",
            ],
            "text": [
                "En nuestra consolidación nacional, las heroicas ciudades de Iquique y Antofagasta han demostrado ser motores vitales para el Norte.",
                "La prosperidad se extiende desde Copiapó hasta la ciudad de Concepción. Es un deber del Estado mirar hacia el sur.",
                "Celebramos nuestro centenario con la mirada en el progreso de Valparaíso y la conectividad ferroviaria que une Santiago con Talca y Chillán.",
                "La nueva constitución protege todas las regiones, asegurando autonomía económica para zonas pujantes como Antofagasta.",
                "La tragedia ha golpeado al sur. Valdivia, Osorno y Concepción requieren nuestra atención máxima.",
                "Iniciamos una época de reencuentro en la república. Desde Arica en el extremo norte, hasta Punta Arenas.",
                "El bicentenario nos encuentra recuperándonos de la adversidad. Las regiones del Biobío, especialmente Concepción y Talcahuano, han sufrido.",
            ],
        }
    )


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    extractor = GeopoliticalExtractor()
    corpus_path = find_corpus()
    if corpus_path is not None:
        resultados = extractor.process_corpus(corpus_path)
        logger.info("Entidades geopolíticas extraídas:\n%s", resultados.head(15))
    else:
        logger.warning("Sin archivo de datos; usando muestra en memoria")
        logger.info("\n%s", create_sample_speeches().to_string())
