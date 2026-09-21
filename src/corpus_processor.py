import os
from typing import List, Dict, Any, Optional

import pandas as pd
import spacy

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
            print(
                f"Cargando fallback NLP. Asegúrese de ejecutar: python -m spacy download {model_size}"
            )
            self.nlp = None

    def process_corpus(self, csv_filepath: str) -> pd.DataFrame:
        """
        Recibe un CSV con discursos históricos y extrae sus menciones espaciales.
        Retorna un DataFrame enriquecido listo para georeferenciación.
        """
        if not self.nlp:
            return pd.DataFrame()

        df = pd.read_csv(csv_filepath)
        extracted_data = []

        for index, row in df.iterrows():
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

    def extract_entities_with_confidence(self, text: str) -> List[Dict[str, Any]]:
        """
        Extrae entidades con información de confianza (start/end positions, label).
        """
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            if ent.label_ in ["LOC", "GPE", "ORG", "PERSON", "NORP"]:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start_char": ent.start_char,
                    "end_char": ent.end_char,
                    "confidence": getattr(ent, "confidence", 1.0),
                })
        
        return entities


def create_sample_speeches() -> pd.DataFrame:
    """Create sample speeches for testing/demo purposes."""
    return pd.DataFrame({
        "year": [1881, 1885, 1910, 1925, 1960, 1990, 2010],
        "speaker": ["Presidente A", "Presidente B", "Presidente C", "Presidente D", 
                    "Presidente E", "Presidente F", "Presidente G"],
        "text": [
            "En nuestra consolidación nacional, las heroicas ciudades de Iquique y Antofagasta han demostrado ser motores vitales para el Norte.",
            "La prosperidad se extiende desde Copiapó hasta la ciudad de Concepción. Es un deber del Estado mirar hacia el sur.",
            "Celebramos nuestro centenario con la mirada en el progreso de Valparaíso y la conectividad ferroviaria que une Santiago con Talca y Chillán.",
            "La nueva constitución protege todas las regiones, asegurando autonomía económica para zonas pujantes como Antofagasta.",
            "La tragedia ha golpeado al sur. Valdivia, Osorno y Concepción requieren nuestra atención máxima.",
            "Iniciamos una época de reencuentro en la república. Desde Arica en el extremo norte, hasta Punta Arenas.",
            "El bicentenario nos encuentra recuperándonos de la adversidad. Las regiones del Biobío, especialmente Concepción y Talcahuano, han sufrido.",
        ]
    })


if __name__ == "__main__":
    # Testeo local aislado
    extractor = GeopoliticalExtractor()
    test_path = os.path.join("data", "processed", "speeches.csv")
    if not os.path.exists(test_path):
        test_path = os.path.join("data", "sample_speeches.csv")
    if os.path.exists(test_path):
        resultados = extractor.process_corpus(test_path)
        print("--- Entidades Geopolíticas Extraídas ---")
        print(resultados.head(15))
    else:
        print("No data file found. Creating sample data...")
        sample_df = create_sample_speeches()
        print(sample_df.to_string())
