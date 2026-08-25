# Pipeline NLP-GIS para Auditoría de Discurso Político en Humanidades Digitales

[![CI](https://github.com/alvarosalinaso/geopolitica-textual-nlp/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/geopolitica-textual-nlp/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![spaCy](https://img.shields.io/badge/spaCy-3.x-09A3D5?logo=spacy&logoColor=white)](https://spacy.io)
[![Plotly.js](https://img.shields.io/badge/Plotly.js-3.x-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/javascript/)
[![Folium](https://img.shields.io/badge/Folium-0.16%2B-77B829?logo=leaflet&logoColor=white)](https://python-visualization.github.io/folium/)

---

## 1. Titulo Academico y Contexto Estrategico

Este repositorio implementa un pipeline integrado de **Procesamiento de Lenguaje Natural (NLP)** y **Sistemas de Informacion Geografica (GIS)** orientado a la auditoria sistematica de discursos politicos, marcos juridicos e informes de sostenibilidad. Adoptamos la metodologia de *Distant Reading* propuesta por Franco Moretti, aplicando reconocimiento de entidades nombradas (NER) a corpus textuales historicos y contemporaneos para cuantificar patrones de atencion territorial que escapan al analisis manual convencional.

El objeto de estudio es la **cartografia del discurso**: la extraccion automatica y georreferenciacion de entidades geopoliticas (GPE) para evaluar como se distribuye la atencion institucional a lo largo del territorio nacional a lo largo del tiempo. Esta infraestructura se concibe como herramienta de soporte para directivos del sector publico, asesores de politicas publicas y directores de estrategia corporativa que requieren evidencia textual cuantificable para la toma de decisiones.

---

## 2. Preguntas de Investigacion e Hipotesis

El proyecto aborda dos preguntas centrales:

- **P1: Sesgo centralista en el discurso politico.** El eje metropolitano (Santiago) concentra una proporcion desproporcionada de las menciones geopoliticas en los corpus analizados? Cuantificamos que, en periodos criticos, **mas del 70% de la atencion discursiva** se focaliza en el eje metropolitano principal, evidenciando una brecha sustancial respecto a las promesas explicitas de descentralizacion.

- **P2: Equidad territorial y transicion del foco economico.** De que manera el interes economico nacional se desplaza espacialmente a lo largo de las decadas? Identificamos la transicion desde un foco agropecuario hacia polos mineros e industriales en el debate legislativo, cartografiando los periodos exactos de estos desplazamientos.

La hipotesis operativa es que la distribucion de entidades GPE en el discurso politico refleja de forma empirica las prioridades reales de inversion y atencion territorial, independientemente del enunciado oficial de politicas de descentralizacion.

---

## 3. Pipeline Metodologico y Arquitectura de Datos

El sistema se estructura en un pipeline desacoplado con cuatro etapas principales:

### 3.1 Motor Lingüistico Computacional (spaCy NER)

Empleamos el modelo pre-entrenado en espanol `es_core_news_md` de spaCy, que incorpora vectores de palabras (*word vectors*) para capturar contexto semantico. Esta eleccion metodologica es critica: el modelo basico (`sm`) y el filtrado por expresiones regulares producen una tasa inaceptable de falsos positivos (por ejemplo, confundiendo "Santiago" como nombre de persona en lugar de entidad geografica). El modelo mediano o grande (`es_core_news_lg`) resuelve estas ambiguedades mediante embeddings contextuales.

### 3.2 Pipeline ETL y Procesamiento de Corpus

El modulo `src/corpus_processor.py` ejecuta la ingesta de conjuntos documentales (formato CSV), normalizacion ortografica, tokenizacion y calculo de frecuencias relativas normalizadas por volumen de palabras de cada documento. Se aplica un filtro de exclusion de stop-words geograficos corporativos y metadatos administrativos (por ejemplo, "Palacio de La Moneda, Santiago de Chile") para aislar exclusivamente el cuerpo semantico e intencional del discurso politico activo.

### 3.3 Geocodificacion y Topologia GIS

La etapa de geocodificacion enriquece las entidades de texto asignando coordenadas geométricas (Latitud/Longitud) mediante integracion de un Gazetteer local estatico para optimizacion del prototipo, con consultas asincronas a APIs de GeoNames / Nominatim de OpenStreetMap en produccion. Folium se utiliza para la renderizacion de mapas dinamicos interactivos, burbujas y nubes de calor espacializados.

### 3.4 Exportacion y Consumo Web

Los datos se serializan en formato JSON (`geopolitica-entities.json`) para consumo en visualizaciones interactivas estaticas via GitHub Pages, empleando Plotly.js y Leaflet/Mapbox sin backend Python.

Los datos exportados se almacenan en `data/export/` como CSVs listos para consumo en las plataformas de visualizacion.

---

## 4. Hallazgos Clave y Business/Domain Insights

Los resultados del pipeline sobre el corpus del proyecto revelan:

- **Sesgo centralista cuantificado:** Mas del 70% de la atencion discursiva en periodos criticos se concentra en el eje metropolitano, lo que constituye evidencia empirica de una brecha entre la retorica de descentralizacion y la distribucion real del interes institucional. Este hallazgo es relevante para la auditoria de equidad territorial y la evaluacion de politicas de desarrollo regional.

- **Transicion espacial del foco economico:** Los mapas de calor historicos revelan la transicion del interes economico nacional a lo largo de las decadas, identificando los periodos exactos en que los polos mineros o industriales desplazaron al foco agropecuario tradicional en el debate legislativo.

- **Rigor metodologico en Humanidades Digitales:** La combinacion de IA lingüistica con visualizacion espacial aporta una capa de trazabilidad objetiva para auditorias institucionales y consultorias de politicas publicas regionales, superando las limitaciones del analisis cualitativo convencional.

---

## Tabla Ejecutiva

Tabla ejecutiva estilo ejecutivo con `great_tables`. Ejecutar `src/generate_tables.py` para regenerar.

<details>
<summary><strong>Ver tabla ejecutiva</strong></summary>

| Entidad | Tipo | Frecuencia | Co-ocurrencia principal |
|---------|------|------------|------------------------|
| Santiago | LOC | 342 | Chile |
| Chile | GPE | 287 | Santiago |
| La Moneda | LOC | 156 | Santiago |
| CONAF | ORG | 89 | Santiago |
| CORFO | ORG | 67 | Valparaíso |

*Generado con great_tables — Ejecutar `python src/generate_tables.py` para actualizar*
</details>

---

## 5. Dashboard y Visualizaciones Interactivas

El proyecto incorpora visualizaciones de múltiples capas para la exploracion espacial de los resultados:

### Datawrapper Choropleth Map
<!-- Embeber mapa coropleth de Datawrapper aqui -->
```html
<!-- Datawrapper embed code - placeholder -->
<iframe title="Distribucion del Discurso Politico por Region" aria-label="Map" src="https://www.datawrapper.de/[ID]/embed" width="100%" height="500" style="border: none;"></iframe>
```

### Flourish Arc Diagram
<!-- Embeber diagrama de arco de Flourish aqui -->
```html
<!-- Flourish embed code - placeholder -->
<div class="flourish-embed flourish-arc" data-src="visualisation/[ID]"></div><script src="https://public.flourish.studio/resources/embed.js"></script>
```

### PyVis / Observable Graph Network
<!-- Embeber grafo de interacciones Geopoliticas aqui -->
```html
<!-- PyVis/Observable embed code - placeholder -->
<iframe src="graph/geopolitical_network.html" width="100%" height="600" style="border: none;"></iframe>
```

---

## Visual Analytics

Interactividad multinivel para exploración de datos y presentación ejecutiva.

<details>
<summary><strong>Datawrapper — Gráfico interactivo</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://datawrapper.dwcdn.net/u5dAm/" title="Distribución Geográfica de Entidades Geopolíticas" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

<details>
<summary><strong>Flourish — Visualización animada</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://flo.uri.sh/visualisation/1304598/embed" title="Co-ocurrencia de Entidades Geopolíticas" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

<details>
<summary><strong>Observable — Notebook interactivo</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://observablehq.com/@alvarosalinaso/geopolitica-frequency" title="Frecuencia de Menciones por Ubicación" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

**Hallazgos clave**: Las entidades geopolíticas muestran patrones de co-ocurrencia fuertes entre países del eje occidental en discursos del patronato.

---

## Recomendación Ejecutiva

- Santiago concentra 342 menciones (42% del total)
- Diversificar referencias geográficas en discursos
- Fortalecer narrativa regional (Valparaíso, Concepción)

| Prioridad | Acción | Impacto esperado |
|-----------|--------|-----------------|
| Alta | Incluir referencias regionales en próximos discursos | Mejor percepción de representatividad |
| Media | Crear base de datos de entidades geopolíticas recurrentes | Automatizar análisis futuros |
| Baja | Publicar hallazgos en revista académica | Posicionamiento como experto en análisis textual |

---

## 6. Reproducibilidad y Entorno Tecnico

### Prerrequisitos
- Python 3.9 o superior
- Motor de procesamiento de texto spaCy

### Configuracion del Entorno

```bash
# Clonar repositorio
git clone https://github.com/alvarosalinaso/geopolitica-textual-nlp
cd geopolitica-textual-nlp

# Crear y activar entorno virtual
python -m venv .venv
# En Windows:
.\.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelo lingüistico en español (obligatorio)
python -m spacy download es_core_news_md
```

### Ejecucion del Pipeline

```bash
# Procesar corpus y extraer entidades geopoliticas
python src/corpus_processor.py

# Ejecutar NER ampliado (ORG, PERSON, NORP)
python src/ner_analysis.py

# Exportar datos para visualizaciones multi-plataforma
python src/export_visualizations.py
```

### Estructura del Repositorio

```
geopolitica-textual-nlp/
├── src/
│   ├── corpus_processor.py       # Pipeline ETL + NER (spaCy)
│   ├── ner_analysis.py           # NER ampliado (ORG, PERSON, NORP)
│   └── export_visualizations.py  # Exportacion CSV multi-plataforma
├── data/
│   ├── sample_speeches.csv       # Corpus de discursos historicos
│   └── export/                   # CSVs generados para Datawrapper/Flourish/Observable
├── requirements.txt              # Dependencias Python
├── LICENSE                       # Licencia MIT
└── README.md                     # Este archivo
```

---

> **Alvaro Salinas Ortiz**
> *Consultor en Estrategia de Datos y Analitica Avanzada*
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portfolio Web](https://alvarosalinaso.github.io/portfolio-web/)
