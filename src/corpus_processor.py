import os

import pandas as pd
import spacy

# Notas de despliegue: Si es primera vez, se debe instalar el modelo de spacy localmente con:
# python -m spacy download es_core_news_md


class GeopoliticalExtractor:
    """
    Motor NLP basado en Arquitectura de Extracción de Entidades (NER).
    Analiza un corpus buscando explícitamente entidades del tipo GPE (Geo-Political Entity)
    y LOC (Locations).
    """

    def __init__(self, model_size="es_core_news_md"):
        # Intentamos cargar el modelo mediano (Medium) por defecto para capturar vectores contextuales sin GPU pesadas
        try:
            self.nlp = spacy.load(model_size)
        except OSError:
            print(
                f"Cargando fallback NLP. Asegúrese de ejecutar: python -m spacy download {model_size}"
            )
            # En un entorno productivo, esto detiene el flujo o fuerza la descarga. Aquí lo aislamos.
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
