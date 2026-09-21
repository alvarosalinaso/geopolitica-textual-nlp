# Arquitectura — geopolitica-textual-nlp

## Visión general
Pipeline NLP para análisis geopolítico de discursos presidenciales chilenos. Extrae entidades (NER), analiza sentimiento, detecta tópicos (LDA), genera mapas interactivos (Folium) y ejecuta tests estadísticos.

## Componentes principales

### Datos
- `data/raw/speeches/` — PDFs de cuentas públicas (1842-2000)
- `data/raw/sample_speeches.csv` — Fallback con textos de ejemplo
- `data/processed/speeches.csv` — Corpus procesado (year, speaker, text)
- `data/export/` — Outputs: ner_entities.json, sentiment_results.json, topics.json, statistical_tests.json, geopolitical_map.html

### Pipeline (src/)
1. `corpus_processor.py` — GeopoliticalExtractor: spaCy NER para entidades LOC/GPE
2. `ner_analysis.py` — run_ner_analysis: NER sobre corpus + archivos de texto
3. `sentiment_analysis.py` — run_sentiment_analysis: TextBlob (lexicon) o OpenAI API
4. `topic_analysis.py` — analyze_topics: bigramas + LDA (sklearn)
5. `geo_analysis.py` — run_geo_analysis: mapa Folium con HeatMap + MarkerCluster
6. `statistical_tests.py` — run_statistical_tests: Chi-cuadrado sobre tipos de entidad
7. `generate_tables.py` — generate: tablas resumen
8. `generate_report.py` — generate_report: reporte consolidado
9. `analyze_all.py` — Orquestador que ejecuta todo el pipeline

### Dashboard
- `dashboard.py` — Dash app con tabs: NER, Sentimiento, Tópicos, Mapa, Estadísticas

## Flujo de datos
```
PDFs/raw CSV → corpus_processor → speeches.csv
speeches.csv → ner_analysis → ner_entities.json
ner_entities.json → geo_analysis → geopolitical_map.html
speeches.csv → sentiment_analysis → sentiment_results.json
speeches.csv → topic_analysis → topics.json
ner_entities.json → statistical_tests → statistical_tests.json
Todos los outputs → generate_report → reporte final
```

## Despliegue
- Render: `gunicorn dashboard:server` (ver `render.yaml`)
- Requiere: spaCy model `es_core_news_sm` (se descarga en build)

## Tests
- `tests/test_corpus_processor.py`
- `tests/test_statistical_tests.py`
- `tests/test_ner_analysis.py`
- `tests/test_sentiment_analysis.py`
- `tests/test_geo_analysis.py`
- `tests/test_topic_analysis.py`
- CI: pytest + coverage + ruff (Python 3.10, 3.11, 3.12)