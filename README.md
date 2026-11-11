# Geopolítica Textual: NLP sobre Mensajes Presidenciales de Chile (1832–2022)

[![CI](https://github.com/alvarosalinaso/geopolitica-textual-nlp/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/geopolitica-textual-nlp/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)

---

## 1. Problema de investigación

¿Cómo hablan los presidentes de Chile del territorio a lo largo de dos siglos?

- **P1. Sesgo centralista:** ¿concentra Santiago una proporción desproporcionada de las
  menciones geopolíticas en los Mensajes Presidenciales ante el Congreso?
- **P2. Desplazamiento espacial:** ¿qué regiones ganan o pierden presencia en el discurso
  a lo largo del tiempo?
- **P3. Tono:** ¿cómo se distribuye la polaridad (positiva/neutral/negativa) de los mensajes?

**Corpus:** 20 Mensajes Presidenciales (uno por gobierno disponible, 1832–2022)
descargados de la Biblioteca del Congreso Nacional (BCN) y extraídos de PDF con
`src/collect_speeches.py`.

---

## 2. Hallazgos y cifras clave

Cifras reproducibles con `python src/key_figures.py` →
`data/export/key_figures.json` (corrida del 2026-10-20, modelo `es_core_news_sm`):

| Indicador | Valor |
|---|---|
| Discursos analizados | **20** (1832–2022) |
| Menciones GPE/LOC | **5.724** |
| Lugares únicos | **3.009** (con ruido del modelo) |
| Menciones de Santiago | **56 (1,0 %)** |
| Entidad más mencionada | **"Chile"** (487) |

- **P1. No hay "dominancia metropolitana":** Santiago concentra ~1 % de las menciones
  geográficas. El discurso presidencial se refiere al país en conjunto ("Chile") mucho
  más que a su capital. La antigua cifra de ">70 %" provenía de datos sintéticos y fue
  retirada.
- **Ruido del NER:** entre los lugares más frecuentes aparecen "Gobierno", "Estado" o
  "Quiero", que son errores de etiquetado de `es_core_news_sm`. Las cifras son una
  **aproximación exploratoria**, no un censo geográfico.

### Qué mide y qué no

- **NER:** reconoce GPE/LOC/ORG/PERSON/NORP sin gold standard ni métricas de evaluación.
  Los modelos de spaCy en español no exponen confianza por entidad y no se fabrica.
- **Geocoding:** solo resuelve los 72 lugares del diccionario estático `GEO_DB`
  (`ENTITY_COORDS` para el mapa Folium). Sin fuzzy matching ni geocoder externo; el log
  informa la cobertura real (`X/Y menciones con coordenadas`).
- **Sentimiento:** léxico español propio y versionado; umbrales ±0.1 **sin calibrar**
  con anotación humana. TextBlob queda solo como referencia secundaria.
- **Tópicos (LDA):** k elegido por coherencia UMass local (medida relativa, no absoluta).
- **Co-ocurrencias** en los diagramas de arcos no implican relaciones diplomáticas ni
  causales.
- **OCR:** el texto conserva los errores de los escaneos de la BCN.

---

## 3. Arquitectura

```
geopolitica-textual-nlp/
├── src/
│   ├── data_loader.py            # Ingesta agnóstica (csv/tsv/parquet/json/xlsx) con pathlib + logging
│   ├── validator.py              # Validación fail-fast de esquemas (corpus, menciones, entidades)
│   ├── metrics.py                # Funciones puras tipadas; división segura (.replace(0, np.nan))
│   ├── logging_config.py         # Configuración central de logging (LOG_LEVEL)
│   ├── collect_speeches.py       # Descarga BCN en runtime + extracción de texto (pdfplumber)
│   ├── corpus_processor.py       # Extractor NER GPE/LOC (spaCy)
│   ├── ner_analysis.py           # NER ampliado (ORG, PERSON, NORP)
│   ├── sentiment_analysis.py     # Sentimiento con léxico español propio
│   ├── topic_analysis.py         # Bigramas + LDA con coherencia UMass
│   ├── geo_analysis.py           # Mapa Folium
│   ├── rag_analysis.py           # Recuperación TF-IDF (+ LLM opcional)
│   ├── statistical_tests.py      # Chi² + V de Cramér
│   ├── key_figures.py            # Cifras clave del README
│   ├── export_visualizations.py  # CSV para Datawrapper / Flourish / Observable
│   └── analyze_all.py            # Orquestador del pipeline
├── scripts/
│   └── generate_synthetic_sample.py  # Muestra sintética determinista para tests
├── tests/                        # pytest (validator, metrics y módulos de análisis)
├── data/
│   ├── raw/speeches/             # PDFs BCN (ignorado por git, se descargan en runtime)
│   ├── processed/speeches.csv    # Corpus extraído (texto + URL de origen + atribución)
│   ├── sample_speeches.csv       # Resúmenes inventados para demo sin red
│   └── export/                   # Salidas del pipeline (ignorado por git)
└── dashboard.py                  # Dashboard Dash (deploy en Render)
```

**Flujo:** `collect_speeches` → `data_loader` + `validator` → NER / sentimiento /
tópicos / geo → `metrics` → exportaciones JSON/CSV → reporte y dashboard.

**Principios:** cero `print()` (todo vía `logging`), rutas con `pathlib.Path`,
validación de esquema antes de procesar y métricas sin efectos secundarios.

---

## 4. Reproducibilidad

Requiere **Python 3.12** (las versiones fijadas en `requirements.txt` lo exigen).

```bash
git clone https://github.com/alvarosalinaso/geopolitica-textual-nlp
cd geopolitica-textual-nlp
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m spacy download es_core_news_sm
```

```bash
python src/collect_speeches.py     # descarga PDFs BCN (carpeta ignorada) y extrae texto
python src/key_figures.py          # cifras clave -> data/export/key_figures.json
python src/analyze_all.py          # pipeline completo -> data/export/
python -m src.export_editorial_data  # CSV para Datawrapper/Flourish -> data/export/editorial/ (ver EMBED_GUIDE.md)
```

Tests y lint (sin red ni PDFs, usan muestra sintética):

```bash
python scripts/generate_synthetic_sample.py   # -> tests/fixtures/synthetic_speeches.csv
pytest tests/ -v
ruff check . && ruff format --check .
```

Nivel de log configurable: `LOG_LEVEL=DEBUG python src/analyze_all.py`.

### Datos, fuentes y licencias

- **Real:** `data/processed/speeches.csv`, texto sin editar de los Mensajes
  Presidenciales de la [BCN, Historia Política](https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes),
  con `source_url` y atribución por fila. Los PDF nunca se commitean.
- **Base legal:** Ley 17.336 (Chile), art. 41: los discursos oficiales de autoridades
  públicas publicados por el Estado pueden reproducirse fielmente.
- **Cobertura:** la BCN no publica 1925; se usa 1926 (mismo gobierno, Emiliano Figueroa).
- **Sintético:** `data/sample_speeches.csv` y la salida de
  `scripts/generate_synthetic_sample.py` son inventados (sin `source_url`) y solo sirven
  para probar el pipeline.

---

## 5. Autor

**Álvaro Salinas Ortiz** | Licenciado en Historia | Business Analytics & Operations

[GitHub](https://github.com/alvarosalinaso)
