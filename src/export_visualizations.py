import os
from pathlib import Path

import pandas as pd

from corpus_processor import GeopoliticalExtractor
from geo_analysis import run_geo_analysis
from ner_analysis import run_ner_analysis
from rag_analysis import run_rag_analysis
from sentiment_analysis import run_sentiment_analysis

# Diccionario de Geocodificación Estática (gacetilla local de ~55 ciudades
# y regiones chilenas). Cobertura limitada: cualquier mención fuera de este
# diccionario se descarta de los mapas/CSVs geográficos (no hay fuzzy matching
# ni Nominatim en este path). Documentado en README "Qué mide y qué no".
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
    grouped.rename(
        columns={"Year": "year", "Mentioned_Location": "location"}, inplace=True
    )

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
            for loc2 in locations[i + 1 :]:
                co_occur = len(
                    set(group[group["Mentioned_Location"] == loc1]["Speaker"].values)
                    & set(group[group["Mentioned_Location"] == loc2]["Speaker"].values)
                )
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
    dataset_path = os.path.join("data", "processed", "speeches.csv")
    if not os.path.exists(dataset_path):
        dataset_path = os.path.join("data", "sample_speeches.csv")

    if not os.path.exists(dataset_path):
        print(f"[✗] No se encontró el dataset: {dataset_path}")
        return

    print("\n[→] Procesando corpus con NLP (spaCy)...")
    extractor = GeopoliticalExtractor(model_size="es_core_news_sm")
    df_places = extractor.process_corpus(dataset_path)

    if df_places.empty:
        print("[✗] No se extrajeron entidades. Verifique el modelo NLP.")
        print("    Comando: python -m spacy download es_core_news_sm")
        return

    print(f"[✓] Corpus procesado: {len(df_places)} menciones extraídas\n")

    # Cobertura del geocoding: qué fracción de menciones tiene coordenadas
    mapped = df_places["Mentioned_Location"].isin(GEO_DB).sum()
    total = len(df_places)
    print(
        f"[i] Geocoding: {mapped}/{total} menciones con coordenadas en el "
        f"diccionario estático ({GEO_DB and len(GEO_DB)} entradas). "
        "Las menciones fuera del diccionario se descartan de mapas/CSVs."
    )

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
    sentiment_results = run_sentiment_analysis(
        data_dir=Path("data"), output_dir=Path(export_dir)
    )
    if sentiment_results:
        print(
            f"[✓] Sentimiento completado: {sentiment_results['n_documents']} documentos analizados"
        )

    print("\n[→] Generando mapa geoespacial Folium...")
    geo_results = run_geo_analysis(
        data_dir=Path("data/export"), output_dir=Path(export_dir)
    )
    if geo_results:
        print(
            f"[✓] Mapa geoespacial completado: {geo_results['entities_plotted']} entidades plotteadas"
        )

    print("\n[→] Ejecutando análisis RAG...")
    rag_results = run_rag_analysis(data_dir=Path("data"), output_dir=Path(export_dir))
    if rag_results:
        print(
            f"[✓] RAG completado: {len(rag_results.get('answers', []))} consultas procesadas"
        )

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
