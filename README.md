# Chilean Political Discourse + NLP

[![CI](https://github.com/alvarosalinaso/geopolitica-textual-nlp/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/geopolitica-textual-nlp/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)

---

## ⚠️ AVISO: qué datos son reales y qué no

**REAL — corpus BCN:** `data/processed/speeches.csv` contiene 20 Mensajes Presidenciales
ante el Congreso (1832–2022) descargados y extraídos de los PDF de la Biblioteca del
Congreso Nacional (BCN) por `src/collect_speeches.py`. Cada fila incluye la URL de origen
(`source_url`) y la atribución a la BCN (`source`). Los PDF **no** se commitean: el script
los descarga en ejecución a `data/raw/speeches/`, carpeta ignorada por git. El texto se
reproduce sin editar, por lo que conserva los errores OCR de los escaneos de la BCN y, en
algunos documentos, los anexos del mensaje.

**SINTÉTICO — demostración:** `data/sample_speeches.csv` son 9 resúmenes inventados para
probar el pipeline sin red. No tienen columnas `source_url`/`source` y no representan
discursos reales.

---

## What is this?

EN: I was curious about how Chilean presidents talk about different regions over time. Does Santiago dominate presidential discourse? How has the economic focus shifted across decades? I built an NLP pipeline to find out.

ES: Me daba curiosidad cómo los presidentes chilenos hablan de distintas regiones a través del tiempo. ¿Domina Santiago el discurso presidencial? ¿Cómo ha cambiado el foco económico en las décadas? Construí un pipeline de NLP para averiguarlo.

---

## Questions I asked

**P1 - Centralist bias:** Does Santiago concentrate a disproportionate share of geopolitical mentions in presidential speeches? On the current real corpus (20 speeches, 1832–2022, `src/key_figures.py`), Santiago has ~1% of GPE/LOC mentions — far from the "dominance" intuition; "Chile" as a whole country mention dominates instead. The old ">70%" figure was based on the synthetic sample and has been removed.

**P2 - Spatial shift:** How does economic interest shift geographically over decades? I mapped the transition from agricultural to mining/industrial focus in legislative debate.

**P3 - Sentiment:** What's the distribution of positive/neutral/negative sentiment in these speeches?

---

## How it works

### 1. NER with spaCy

Uses `es_core_news_sm` (small Spanish model) for Named Entity Recognition. The small model is faster and lighter for deployment while providing usable GPE/LOC entity recognition (noisy — see "Qué mide y qué no").

### 2. Corpus processing

`src/corpus_processor.py` ingests CSV speeches, normalizes text, tokenizes, and calculates relative frequencies normalized by document word count.

### 3. Geocoding + Folium maps

Geocoding con diccionarios estáticos locales: `GEO_DB` (72 ciudades y regiones
chilenas en `src/export_visualizations.py`) para los CSVs de exportación, y
`ENTITY_COORDS` en `geo_analysis.py` para el mapa Folium. **No hay geocoder
externo** (sin Nominatim ni otras APIs de geocoding).

#### Qué mide y qué no (geocoding)

- **Mide**: frecuencia de las entidades GPE/LOC que el modelo spaCy reconoce **y** que
  existen en los diccionarios estáticos del repo (`GEO_DB` para los CSVs de exportación;
  `ENTITY_COORDS` para el mapa Folium).
- **No mide**: el territorio completo mencionado. Toda mención fuera del diccionario
  (72 entradas en `GEO_DB`) se descarta de los CSVs y mapas; no hay fuzzy matching.
  Una mención como "el Norte Grande" o "la Zona Central" no tiene coordenada y desaparece.
- **Sesgos conocidos**: el modelo `es_core_news_sm` confunde a veces personas (PERSON)
  con lugares (GPE), y el texto fuente tiene OCR de los escaneos de la BCN. Los
  resultados son una **aproximación exploratoria**, no un inventario geográfico completo.
- El script imprime la cobertura real (`X/Y menciones con coordenadas`) en cada corrida.

### 4. Sentiment analysis

`src/sentiment_analysis.py` usa un léxico español propio y versionado en el repo
(método primario, sin llamadas de red ni APIs externas). TextBlob queda solo como
referencia secundaria: su léxico está entrenado en inglés y no está validado para
español. **Los umbrales ±0.1 (positivo/negativo/neutral) son heurísticos y no están
calibrados con anotación humana** — ver "Qué mide y qué no".

---

## Qué mide y qué no

Resumen de alcance y límites de cada componente (las secciones de "How it works"
detallan el geocoding):

- **NER (`es_core_news_sm`)**: reconoce entidades GPE/LOC/ORG/PERSON/NORP de forma
  ruidosa, sin gold standard ni métricas de evaluación en este repo. Atributos como
  "confianza" no existen en los modelos en español y no se fabrican.
- **Sentimiento**: léxico español propio con umbrales ±0.1 **sin calibrar** (no hay
  anotación humana de referencia). TextBlob es solo comparación secundaria, no un
  baseline validado para español.
- **Tópicos (LDA)**: número de tópicos elegido por grilla con coherencia UMass
  implementada localmente (referencia relativa entre corridas, no una medida absoluta
  de calidad). Las etiquetas de tópico son palabras más probables, no interpretaciones
  humanas.
- **Geocoding**: solo resuelve lo que está en los diccionarios estáticos del repo
  (72 entradas en `GEO_DB`; `ENTITY_COORDS` para el mapa Folium); sin fuzzy matching ni
  geocoder externo. El script imprime la cobertura real (`X/Y menciones con coordenadas`).
- **Corpus**: 20 Mensajes BCN (1832–2022, uno por gobierno disponible), con OCR heredado
  de los escaneos; no es un inventario continuo ni representativo de todo el discurso
  presidencial.

---

## Fuentes y licencias

- **Fuente del corpus**: Biblioteca del Congreso Nacional de Chile (BCN) — Historia
  Política, *Mensajes Presidenciales ante el Congreso Pleno*:
  <https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes>
- **Base legal del texto**: Ley 17.336 de Propiedad Intelectual (Chile), art. 41 — "quedan
  excluidas de la protección de la presente ley [...] cualquier documento público del Estado,
  tales como [...] discursos oficiales de autoridades públicas [...], cuya reproducción será
  lícita después de publicadas por el Estado y siempre que obedezcan fielmente al texto
  original". Por eso el repositorio guarda el texto extraído (sin editar) con URL de origen
  y atribución, y nunca los PDF.
- **Cobertura declarada**: la selección curada cubre 1832–2022 (un mensaje por gobierno en
  la medida en que la BCN lo publica). El índice de la BCN **no publica 1925**; se usa 1926
  (mismo gobierno, Emiliano Figueroa) y queda documentado en `src/collect_speeches.py`.
- **Muestra sintética**: `data/sample_speeches.csv` es inventada (demo del pipeline) y se
  distingue del corpus real porque no tiene `source_url`/`source`.

---

## Key findings (sobre corpus real BCN, corrida de `src/key_figures.py`)

Cifras reproducibles: ejecuta `python src/key_figures.py` (requiere el corpus real
de `collect_speeches.py`) y consulta `data/export/key_figures.json`. Los valores
de abajo son de la corrida del 2026-10-20 sobre los 20 discursos BCN:

- **5.724 menciones GPE/LOC** en total (3.009 formas únicas, con ruido del modelo:
  entidades como "Gobierno" o "Estado" a veces se etiquetan como lugar).
- **Santiago: 56 menciones (1.0%)** — no hay "dominancia metropolitana" en este
  corpus; la forma dominante es la mención del país ("Chile", 487). (56 incluye
  el alias "Santiago de Chile"; solo "Santiago" exacto son 53 — ver
  `key_figures.json`.)
- El modelo `es_core_news_sm` comete errores de etiquetado; los resultados son una
  **aproximación exploratoria**, no un censo geográfico.

> **Nota**: los "hallazgos" anteriores ("342 menciones, 42%", ">70%", "alianzas
> geopolíticas") provenían del corpus sintético y no se reproducen con datos reales;
> fueron reemplazados por estas cifras con script verificable. "Co-ocurrencias" en los
> diagramas de arcos no implican relaciones diplomáticas ni causales.

---

## Visualizations

<details>
<summary><strong>Datawrapper — Geographic distribution</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://datawrapper.dwcdn.net/u5dAm/" title="Entity Distribution Map" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

<details>
<summary><strong>Observable — Frequency by location</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://observablehq.com/@alvarosalinaso/geopolitica-frequency" title="Mention Frequency" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

---

## How to run

```bash
git clone https://github.com/alvarosalinaso/geopolitica-textual-nlp
cd geopolitica-textual-nlp
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m spacy download es_core_news_sm

python src/collect_speeches.py   # descarga PDFs de BCN (a carpeta ignorada) y extrae texto
python src/corpus_processor.py
python src/ner_analysis.py
python src/sentiment_analysis.py
python src/export_visualizations.py
```

---

## Project structure

```
geopolitica-textual-nlp/
├── src/
│   ├── collect_speeches.py       # Descarga corpus BCN en runtime + extracción de texto
│   ├── corpus_processor.py       # ETL + NER (spaCy)
│   ├── ner_analysis.py           # Extended NER (ORG, PERSON, NORP)
│   ├── sentiment_analysis.py     # Sentiment (léxico ES propio; TextBlob secundario)
│   ├── rag_analysis.py           # RAG: TF-IDF + LLM
│   ├── geo_analysis.py           # Folium interactive map
│   └── export_visualizations.py  # CSV export for multi-platform viz
├── data/
│   ├── raw/speeches/             # PDFs de BCN — se descargan en runtime, ignorados por git
│   └── processed/speeches.csv    # Texto extraído real (BCN) + URL origen y atribución
└── requirements.txt
```

---

## Related projects

- [Chile Geografía Histórica](https://github.com/alvarosalinaso/chile-geografia-historica) — Interactive map of Chile's historical geography
- [Chilean Video Games](https://github.com/alvarosalinaso/chilean-videogames-analysis) — Market analysis of Chilean indie games
- [Portfolio Web](https://github.com/alvarosalinaso/portfolio-web) — Dashboard with all projects

---

> **Álvaro Salinas Ortiz**
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portfolio](https://alvarosalinaso.github.io/portfolio-web/)
