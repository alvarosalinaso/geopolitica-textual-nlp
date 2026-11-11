"""Exporta CSVs y snippets para Datawrapper, Flourish y Observable.

Orquesta además NER ampliado, sentimiento, mapa Folium, RAG, tests
estadísticos, tabla ejecutiva y reporte.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

try:
    from src.corpus_processor import GeopoliticalExtractor
    from src.data_loader import EXPORT_DIR, find_corpus
    from src.geo_analysis import run_geo_analysis
    from src.metrics import century_label, location_frequency_stats
    from src.ner_analysis import run_ner_analysis
    from src.rag_analysis import run_rag_analysis
    from src.sentiment_analysis import run_sentiment_analysis
    from src.validator import validate_places
except ImportError:  # ejecución directa: python src/export_visualizations.py
    from corpus_processor import GeopoliticalExtractor
    from data_loader import EXPORT_DIR, find_corpus
    from geo_analysis import run_geo_analysis
    from metrics import century_label, location_frequency_stats
    from ner_analysis import run_ner_analysis
    from rag_analysis import run_rag_analysis
    from sentiment_analysis import run_sentiment_analysis
    from validator import validate_places

logger = logging.getLogger(__name__)

# Diccionario de Geocodificación Estática: 72 ciudades y regiones chilenas
# (gacetilla local, sin fuzzy matching ni geocoder externo). Cobertura limitada:
# cualquier mención fuera de este diccionario se descarta de los mapas/CSVs
# geográficos. Documentado en README "Qué mide y qué no".
GEO_DB = {
    # Ciudades
    "Arica": [-18.4783, -70.3126],
    "Iquique": [-20.2133, -70.1503],
    "Pozo Almonte": [-20.2597, -69.8861],
    "Antofagasta": [-23.6500, -70.4000],
    "Mejillones": [-23.0992, -70.4467],
    "Calama": [-22.4536, -68.9264],
    "Taltal": [-25.4100, -70.4900],
    "Chañaral": [-26.3467, -70.6200],
    "Copiapó": [-27.3667, -70.3333],
    "Vallenar": [-28.5762, -70.7570],
    "La Serena": [-29.9027, -71.2520],
    "Coquimbo": [-29.9533, -71.3394],
    "Ovalle": [-30.6011, -71.1932],
    "Illapel": [-31.6333, -71.1667],
    "San Felipe": [-32.7500, -70.7283],
    "Los Andes": [-32.8333, -70.5833],
    "Valparaíso": [-33.0456, -71.6231],
    "Viña del Mar": [-33.0246, -71.5518],
    "Quillota": [-32.8800, -71.2494],
    "San Antonio": [-33.5947, -71.6127],
    "Santiago": [-33.4489, -70.6693],
    "Rancagua": [-34.1708, -70.7408],
    "San Fernando": [-34.5891, -70.9931],
    "Santa Cruz": [-34.6333, -71.3167],
    "Curicó": [-34.9828, -71.2394],
    "Molina": [-35.1133, -71.2833],
    "Talca": [-35.4264, -71.6554],
    "San Javier": [-35.5958, -71.7433],
    "Linares": [-35.8500, -71.6000],
    "Cauquenes": [-35.9700, -72.3200],
    "Constitución": [-35.3333, -72.4167],
    "Parral": [-36.1433, -71.8250],
    "Chillán": [-36.6063, -72.1034],
    "Los Ángeles": [-37.4667, -72.3500],
    "Tomé": [-36.6167, -72.9500],
    "Coronel": [-37.0333, -73.2167],
    "Concepción": [-36.8270, -73.0503],
    "Talcahuano": [-36.7167, -73.1167],
    "Angol": [-37.7964, -72.7161],
    "Temuco": [-38.7359, -72.5904],
    "Villarrica": [-39.2833, -72.2167],
    "Pucón": [-39.2667, -71.9667],
    "Valdivia": [-39.8142, -73.2459],
    "Osorno": [-40.5739, -73.1336],
    "Puerto Varas": [-41.3167, -72.9833],
    "Puerto Montt": [-41.4693, -72.9424],
    "Castro": [-42.4808, -73.7667],
    "Ancud": [-41.8697, -73.8262],
    "Coyhaique": [-45.5717, -72.0669],
    "Puerto Aysén": [-45.4000, -72.7000],
    "Chile Chico": [-46.5400, -71.7300],
    "Punta Arenas": [-53.1500, -70.9167],
    "Porvenir": [-53.2949, -70.3677],
    "Puerto Natales": [-51.7236, -72.5100],
    # Regiones / provincias históricas mencionadas en discursos
    # (Antofagasta, Coquimbo y Valparaíso ya están como ciudad arriba)
    "Arica y Parinacota": [-18.4783, -70.3126],
    "Tarapacá": [-20.2133, -70.1503],
    "Atacama": [-27.3667, -70.3333],
    "Aconcagua": [-32.8333, -70.5833],
    "Metropolitana": [-33.4489, -70.6693],
    "O'Higgins": [-34.1708, -70.7408],
    "Colchagua": [-34.6333, -71.3167],
    "Maule": [-35.4264, -71.6554],
    "Ñuble": [-36.6063, -72.1034],
    "Biobío": [-36.8270, -73.0503],
    "Araucanía": [-38.7359, -72.5904],
    "Los Ríos": [-39.8142, -73.2459],
    "Los Lagos": [-41.4693, -72.9424],
    "Llanquihue": [-41.4693, -72.9424],
    "Chiloé": [-42.4808, -73.7667],
    "Aysén": [-45.5717, -72.0669],
    "Magallanes": [-53.1500, -70.9167],
    "Patagonia": [-46.5400, -71.7300],
}


def ensure_export_dir(export_dir: Path = EXPORT_DIR) -> Path:
    """Crea el directorio de exportación si no existe."""
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def _with_coords(df_places: pd.DataFrame) -> pd.DataFrame:
    """Filtra menciones presentes en GEO_DB y agrega lat/lon."""
    validate_places(df_places)
    df = df_places.copy()
    df["Coords"] = df["Mentioned_Location"].map(GEO_DB)
    df_valid = df.dropna(subset=["Coords"]).copy()
    df_valid["lat"] = df_valid["Coords"].apply(lambda x: x[0])
    df_valid["lon"] = df_valid["Coords"].apply(lambda x: x[1])
    return df_valid


def generate_dw_choropleth_temporal(
    df_places: pd.DataFrame, export_dir: Path | str
) -> pd.DataFrame:
    """
    Genera data/export/dw_choropleth_temporal.csv
    Columnas: year, location, mentions, lat, lon
    """
    df_valid = _with_coords(df_places)
    grouped = (
        df_valid.groupby(["Year", "Mentioned_Location", "lat", "lon"])
        .size()
        .reset_index(name="mentions")
        .rename(columns={"Year": "year", "Mentioned_Location": "location"})
    )

    output_path = Path(export_dir) / "dw_choropleth_temporal.csv"
    grouped.to_csv(output_path, index=False)
    logger.info("Generado: %s (%d filas)", output_path, len(grouped))
    return grouped


def generate_flourish_arc_geopolitica(
    df_places: pd.DataFrame, export_dir: Path | str
) -> pd.DataFrame:
    """
    Genera data/export/flourish_arc_geopolitica.csv
    Columnas: source_location, target_location, co_occurrences, year
    """
    df_valid = _with_coords(df_places)

    arcs = []
    for year, group in df_valid.groupby("Year"):
        speakers_by_loc = group.groupby("Mentioned_Location")["Speaker"].agg(set)
        locations = group["Mentioned_Location"].unique()
        for i, loc1 in enumerate(locations):
            for loc2 in locations[i + 1 :]:
                co_occur = len(speakers_by_loc[loc1] & speakers_by_loc[loc2])
                if co_occur > 0:
                    arcs.append(
                        {
                            "source_location": loc1,
                            "target_location": loc2,
                            "co_occurrences": co_occur,
                            "year": year,
                        }
                    )

    df_arcs = pd.DataFrame(arcs)
    output_path = Path(export_dir) / "flourish_arc_geopolitica.csv"
    df_arcs.to_csv(output_path, index=False)
    logger.info("Generado: %s (%d filas)", output_path, len(df_arcs))
    return df_arcs


def generate_observable_frecuencias(
    df_places: pd.DataFrame, export_dir: Path | str
) -> pd.DataFrame:
    """
    Genera data/export/observable_frecuencias.csv
    Columnas: location, total_mentions, speeches, avg_per_speech, century
    """
    df_valid = _with_coords(df_places)
    stats = location_frequency_stats(df_valid)

    df_valid["century"] = df_valid["Year"].apply(century_label)
    dominant_century = (
        df_valid.groupby("Mentioned_Location")["century"]
        .agg(lambda x: x.value_counts().index[0])
        .reset_index()
    )
    stats = stats.merge(dominant_century, on="Mentioned_Location", how="left")
    stats = stats.rename(columns={"Mentioned_Location": "location"})

    output_path = Path(export_dir) / "observable_frecuencias.csv"
    stats.to_csv(output_path, index=False)
    logger.info("Generado: %s (%d filas)", output_path, len(stats))
    return stats


def generate_embed_snippets(export_dir: Path | str) -> Path:
    """Genera data/export/embed_snippets.md con snippets HTML embebibles."""
    md_content = """# Snippets de Visualización Incrustable

## 1. Datawrapper Choropleth Map
```html
<div class="datawrapper-chart" style="width: 100%; max-width: 800px; margin: auto;">
  <iframe
    src="https://datawrapper.dwcdn.net/SIMPLIFICAR_ID/"
    title="Choropleth Temporal - Menciones por Año y Ubicación"
    style="width: 100%; border: none;"
    height="500"
    loading="lazy">
  </iframe>
  <p style="font-size: 0.8em; color: #666; text-align: center;">
    Datos: dw_choropleth_temporal.csv | Motor NLP: spaCy (es_core_news_sm)
  </p>
</div>
```

## 2. Flourish Arc Diagram (Co-ocurrencias de Ubicaciones)
```html
<div class="flourish-chart" style="width: 100%; max-width: 900px; margin: auto;">
  <div
    class="flourish-embed flourish-arc-diagram"
    data-src="visualisation/SIMPLIFICAR_ID/"
    data-url="https://flo.uri.sh/visualisation/SIMPLIFICAR_ID/embed"
    style="width: 100%; border: 1px solid #ccc;">
  </div>
  <script src="https://public.flourish.studio/resources/embed.js"></script>
  <p style="font-size: 0.8em; color: #666; text-align: center;">
    Datos: flourish_arc_geopolitica.csv | Co-ocurrencias por hablante y año
  </p>
</div>
```

## 3. Observable Bar Chart (Análisis de Frecuencias)
```html
<div class="observable-chart" style="width: 100%; max-width: 800px; margin: auto;">
  <figure>
    <iframe
      src="https://observablehq.com/embed/@USUARIO/SIMPLIFICAR_VIZ"
      title="Frecuencia Territorial por Ubicación"
      style="width: 100%; border: none; min-height: 400px;"
      loading="lazy">
    </iframe>
    <figcaption style="font-size: 0.8em; color: #666; text-align: center;">
      Datos: observable_frecuencias.csv | Total de menciones y promedio por discurso
    </figcaption>
  </figure>
</div>
```

---

### Notas de Uso
1. Reemplace `SIMPLIFICAR_ID` / `@USUARIO/SIMPLIFICAR_VIZ` con sus IDs reales tras subir los CSV a cada plataforma.
2. Los CSV generados en `data/export/` son la fuente de datos para cada visualización.
3. Para incrustar en cualquier plataforma web, utilice los snippets HTML proporcionados.
"""
    output_path = Path(export_dir) / "embed_snippets.md"
    output_path.write_text(md_content, encoding="utf-8")
    logger.info("Generado: %s", output_path)
    return output_path


def main() -> None:
    """Procesa el corpus y genera todos los archivos de exportación."""
    logger.info("Generación de visualizaciones para Geopolítica Textual")

    export_dir = ensure_export_dir()
    dataset_path = find_corpus()
    if dataset_path is None:
        logger.error("No se encontró dataset en data/processed ni muestra sintética")
        return

    logger.info("Procesando corpus con NLP (spaCy): %s", dataset_path)
    extractor = GeopoliticalExtractor(model_size="es_core_news_sm")
    df_places = extractor.process_corpus(dataset_path)

    if df_places.empty:
        logger.error(
            "No se extrajeron entidades. Ejecuta: python -m spacy download "
            "es_core_news_sm"
        )
        return

    logger.info("Corpus procesado: %d menciones extraídas", len(df_places))

    # Cobertura del geocoding: qué fracción de menciones tiene coordenadas
    mapped = int(df_places["Mentioned_Location"].isin(GEO_DB).sum())
    logger.info(
        "Geocoding: %d/%d menciones con coordenadas en el diccionario estático "
        "(%d entradas). Las menciones fuera del diccionario se descartan.",
        mapped,
        len(df_places),
        len(GEO_DB),
    )

    generate_dw_choropleth_temporal(df_places, export_dir)
    generate_flourish_arc_geopolitica(df_places, export_dir)
    generate_observable_frecuencias(df_places, export_dir)
    generate_embed_snippets(export_dir)

    logger.info("Ejecutando NER ampliado (ORG, PERSON, NORP)...")
    ner_results = run_ner_analysis(data_dir=Path("data"), output_dir=export_dir)
    if ner_results:
        logger.info("NER completado: %d entidades totales", ner_results["total"])

    logger.info("Ejecutando análisis de sentimiento...")
    sentiment_results = run_sentiment_analysis(
        data_dir=Path("data"), output_dir=export_dir
    )
    if sentiment_results:
        logger.info(
            "Sentimiento completado: %d documentos analizados",
            sentiment_results["n_documents"],
        )

    logger.info("Generando mapa geoespacial Folium...")
    geo_results = run_geo_analysis(data_dir=export_dir, output_dir=export_dir)
    if geo_results:
        logger.info(
            "Mapa completado: %d entidades plotteadas", geo_results["entities_plotted"]
        )

    logger.info("Ejecutando análisis RAG...")
    rag_results = run_rag_analysis(data_dir=Path("data"), output_dir=export_dir)
    if rag_results:
        logger.info(
            "RAG completado: %d consultas procesadas",
            len(rag_results.get("answers", [])),
        )

    try:
        from src.generate_report import generate_report
        from src.generate_tables import generate as generate_exec_tables
        from src.statistical_tests import run_statistical_tests
    except ImportError:
        from generate_report import generate_report
        from generate_tables import generate as generate_exec_tables
        from statistical_tests import run_statistical_tests

    run_statistical_tests(data_dir=export_dir, output_dir=export_dir)
    generate_exec_tables()
    generate_report(output_dir=export_dir)

    logger.info("Exportación completada en %s", export_dir)


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    main()
