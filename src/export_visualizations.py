import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.corpus_processor import GeopoliticalExtractor
from src.ner_analysis import run_ner_analysis
from src.sentiment_analysis import run_sentiment_analysis
from src.geo_analysis import run_geo_analysis
from src.rag_analysis import run_rag_analysis

# Diccionario de Geocodificación Estática (mismo que en app_mapas.py)
GEO_DB = {
    "Iquique": [-20.2133, -70.1503],
    "Antofagasta": [-23.6500, -70.4000],
    "Copiapó": [-27.3667, -70.3333],
    "Valparaíso": [-33.0456, -71.6231],
    "Santiago": [-33.4489, -70.6693],
    "Talca": [-35.4264, -71.6554],
    "Chillán": [-36.6063, -72.1034],
    "Concepción": [-36.8270, -73.0503],
    "Talcahuano": [-36.7167, -73.1167],
    "Valdivia": [-39.8142, -73.2459],
    "Osorno": [-40.5739, -73.1336],
    "Puerto Montt": [-41.4693, -72.9424],
    "Punta Arenas": [-53.1500, -70.9167],
    "Arica": [-18.4783, -70.3126],
    "Biobío": [-37.4667, -72.3500],
}


def ensure_export_dir():
    """Crea el directorio data/export si no existe."""
    export_dir = os.path.join("data", "export")
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def generate_dw_choropleth_temporal(df_places, export_dir):
    """
    Genera data/export/dw_choropleth_temporal.csv
    Columnas: year, location, mentions, lat, lon
    """
    df = df_places.copy()
    df["Coords"] = df["Mentioned_Location"].map(GEO_DB)
    df_valid = df.dropna(subset=["Coords"]).copy()
    df_valid["lat"] = df_valid["Coords"].apply(lambda x: x[0])
    df_valid["lon"] = df_valid["Coords"].apply(lambda x: x[1])

    grouped = (
        df_valid.groupby(["Year", "Mentioned_Location", "lat", "lon"])
        .size()
        .reset_index(name="mentions")
    )
    grouped.rename(columns={"Year": "year", "Mentioned_Location": "location"}, inplace=True)

    output_path = os.path.join(export_dir, "dw_choropleth_temporal.csv")
    grouped.to_csv(output_path, index=False)
    print(f"[✓] Generado: {output_path} ({len(grouped)} filas)")
    return grouped


def generate_flourish_arc_geopolitica(df_places, export_dir):
    """
    Genera data/export/flourish_arc_geopolitica.csv
    Columnas: source_location, target_location, co_occurrences, year
    """
    df = df_places.copy()
    df["Coords"] = df["Mentioned_Location"].map(GEO_DB)
    df_valid = df.dropna(subset=["Coords"]).copy()

    arcs = []
    for year, group in df_valid.groupby("Year"):
        locations = group["Mentioned_Location"].unique()
        for i, loc1 in enumerate(locations):
            for loc2 in locations[i + 1:]:
                co_occur = len(
                    set(group[group["Mentioned_Location"] == loc1]["Speaker"].values)
                    & set(group[group["Mentioned_Location"] == loc2]["Speaker"].values)
                )
                if co_occur > 0:
                    arcs.append({
                        "source_location": loc1,
                        "target_location": loc2,
                        "co_occurrences": co_occur,
                        "year": year,
                    })

    df_arcs = pd.DataFrame(arcs)
    output_path = os.path.join(export_dir, "flourish_arc_geopolitica.csv")
    df_arcs.to_csv(output_path, index=False)
    print(f"[✓] Generado: {output_path} ({len(df_arcs)} filas)")
    return df_arcs


def generate_observable_frecuencias(df_places, export_dir):
    """
    Genera data/export/observable_frecuencias.csv
    Columnas: location, total_mentions, avg_per_speech, century
    """
    df = df_places.copy()
    df["Coords"] = df["Mentioned_Location"].map(GEO_DB)
    df_valid = df.dropna(subset=["Coords"]).copy()

    stats = (
        df_valid.groupby("Mentioned_Location")
        .agg(
            total_mentions=("Mentioned_Location", "count"),
            speeches=("Year", "nunique"),
        )
        .reset_index()
    )
    stats["avg_per_speech"] = (stats["total_mentions"] / stats["speeches"]).round(2)

    def get_century(year):
        return f"{(year // 100) + 1}th"

    df_valid["century"] = df_valid["Year"].apply(get_century)
    dominant_century = (
        df_valid.groupby("Mentioned_Location")["century"]
        .agg(lambda x: x.value_counts().index[0])
        .reset_index()
    )
    stats = stats.merge(dominant_century, on="Mentioned_Location", how="left")
    stats.rename(
        columns={
            "Mentioned_Location": "location",
            "century": "century",
        },
        inplace=True,
    )

    output_path = os.path.join(export_dir, "observable_frecuencias.csv")
    stats.to_csv(output_path, index=False)
    print(f"[✓] Generado: {output_path} ({len(stats)} filas)")
    return stats


def generate_embed_snippets(export_dir):
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
    Datos: dw_choropleth_temporal.csv | Motor NLP: spaCy (es_core_news_md)
  </p>
</div>
```

## 2. Flourish Arc Diagram (Relaciones entre Ubicaciones)
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
    output_path = os.path.join(export_dir, "embed_snippets.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[✓] Generado: {output_path}")
    return output_path


def main():
    """Función principal: procesa corpus y genera todos los archivos de exportación."""
    print("=" * 60)
    print("  Generación de Visualizaciones para Geopolítica Textual")
    print("=" * 60)

    export_dir = ensure_export_dir()
    dataset_path = os.path.join("data", "sample_speeches.csv")

    if not os.path.exists(dataset_path):
        print(f"[✗] No se encontró el dataset: {dataset_path}")
        return

    print("\n[→] Procesando corpus con NLP (spaCy)...")
    extractor = GeopoliticalExtractor(model_size="es_core_news_md")
    df_places = extractor.process_corpus(dataset_path)

    if df_places.empty:
        print("[✗] No se extrajeron entidades. Verifique el modelo NLP.")
        print("    Comando: python -m spacy download es_core_news_md")
        return

    print(f"[✓] Corpus procesado: {len(df_places)} menciones extraídas\n")

    print("[→] Generando CSV para Datawrapper...")
    generate_dw_choropleth_temporal(df_places, export_dir)

    print("[→] Generando CSV para Flourish...")
    generate_flourish_arc_geopolitica(df_places, export_dir)

    print("[→] Generando CSV para Observable...")
    generate_observable_frecuencias(df_places, export_dir)

    print("\n[→] Generando snippets de incrustación...")
    generate_embed_snippets(export_dir)

    print("\n[→] Ejecutando NER ampliado (ORG, PERSON, NORP)...")
    ner_results = run_ner_analysis(data_dir=Path("data"), output_dir=Path(export_dir))
    if ner_results:
        print(f"[✓] NER completado: {ner_results['total']} entidades totales")

    print("\n[→] Ejecutando análisis de sentimiento...")
    sentiment_results = run_sentiment_analysis(data_dir=Path("data"), output_dir=Path(export_dir))
    if sentiment_results:
        print(f"[✓] Sentimiento completado: {sentiment_results['n_documents']} documentos analizados")

    print("\n[→] Generando mapa geoespacial Folium...")
    geo_results = run_geo_analysis(data_dir=Path("data/export"), output_dir=Path(export_dir))
    if geo_results:
        print(f"[✓] Mapa geoespacial completado: {geo_results['entities_plotted']} entidades plotteadas")

    print("\n[→] Ejecutando análisis RAG...")
    rag_results = run_rag_analysis(data_dir=Path("data"), output_dir=Path(export_dir))
    if rag_results:
        print(f"[✓] RAG completado: {len(rag_results.get('answers', []))} consultas procesadas")

    # Statistical tests
    from statistical_tests import run_statistical_tests
    run_statistical_tests()

    # Generate executive tables
    from generate_tables import generate as generate_exec_tables
    generate_exec_tables()

    # Generate paper report
    from generate_report import generate_report
    generate_report()

    print("\n" + "=" * 60)
    print("  ¡Exportación completada!")
    print(f"  Archivos generados en: {export_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
