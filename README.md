# Chilean Political Discourse + NLP

[![CI](https://github.com/alvarosalinaso/geopolitica-textual-nlp/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/geopolitica-textual-nlp/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)

---

## What is this?

EN: I was curious about how Chilean presidents talk about different regions over time. Does Santiago dominate presidential discourse? How has the economic focus shifted across decades? I built an NLP pipeline to find out.

ES: Me daba curiosidad cómo los presidentes chilenos hablan de distintas regiones a través del tiempo. ¿Domina Santiago el discurso presidencial? ¿Cómo ha cambiado el foco económico en las décadas? Construí un pipeline de NLP para averiguarlo.

---

## Questions I asked

**P1 - Centralist bias:** Does Santiago concentrate a disproportionate share of geopolitical mentions in presidential speeches? I found that in critical periods, over 70% of discursive attention focuses on the metropolitan axis.

**P2 - Spatial shift:** How does economic interest shift geographically over decades? I mapped the transition from agricultural to mining/industrial focus in legislative debate.

**P3 - Sentiment:** What's the distribution of positive/neutral/negative sentiment in these speeches?

---

## How it works

### 1. NER with spaCy

Uses `es_core_news_md` (medium Spanish model with word vectors) for Named Entity Recognition. The medium model resolves ambiguities that the small model misses (e.g., "Santiago" as location vs. person name).

### 2. Corpus processing

`src/corpus_processor.py` ingests CSV speeches, normalizes text, tokenizes, and calculates relative frequencies normalized by document word count.

### 3. Geocoding + Folium maps

Geocodes entities using a local Gazetteer + Nominatim API. Renders interactive maps with Folium (heatmaps, bubble maps).

### 4. Sentiment analysis

OpenAI API or TextBlob fallback for sentiment scoring on each speech.

---

## Key findings

- Santiago concentrates 342 mentions (42% of total) — strong centralist bias
- Historical heatmaps show the shift from agricultural to mining/industrial focus
- Entity co-occurrence patterns reveal geopolitical alliances in presidential discourse

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
python -m spacy download es_core_news_md

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
│   ├── corpus_processor.py       # ETL + NER (spaCy)
│   ├── ner_analysis.py           # Extended NER (ORG, PERSON, NORP)
│   ├── sentiment_analysis.py     # Sentiment (OpenAI/TextBlob)
│   ├── rag_analysis.py           # RAG: TF-IDF + LLM
│   ├── geo_analysis.py           # Folium interactive map
│   └── export_visualizations.py  # CSV export for multi-platform viz
├── data/
│   ├── raw/speeches/             # Source PDFs/HTML from BCN
│   └── processed/speeches.csv    # Extracted speeches
└── requirements.txt
```

---

> **Álvaro Salinas Ortiz**
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portfolio](https://alvarosalinaso.github.io/portfolio-web/)
