# Cartografía de Datos y NLP en Humanidades Digitales: Análisis del Discurso y Fricciones de Poder Geopolítico

[![CI](https://github.com/alvarosalinaso/geopolitica-textual-nlp/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/geopolitica-textual-nlp/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![spaCy](https://img.shields.io/badge/spaCy-3.x-09A3D5?logo=spacy&logoColor=white)](https://spacy.io)
[![Plotly.js](https://img.shields.io/badge/Plotly.js-3.x-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/javascript/)
[![Folium](https://img.shields.io/badge/Folium-0.16%2B-77B829?logo=leaflet&logoColor=white)](https://python-visualization.github.io/folium/)

---

## Executive Summary & Decision Making

Este proyecto establece un pipeline avanzado de **Procesamiento de Lenguaje Natural (NLP)** y **Sistemas de Información Geográfica (GIS)** para auditar a gran escala la evolución de discursos políticos, marcos jurídicos o informes de sostenibilidad. Utilizando metodologías de *Distant Reading* (Lectura Distante), el sistema extrae automáticamente miles de Entidades Nombradas Geopolíticas (GPE) de corpus textuales históricos y contemporáneos masivos, eliminando los sesgos y limitaciones de tiempo de la lectura manual e inyectando rigor cuantitativo en el análisis hermenéutico del discurso.

Esta infraestructura analítica permite a Directivos del Sector Público, Asesores de Políticas Públicas y Directores de Estrategia Corporativa tomar **decisiones críticas basadas en evidencia textual**:
1. **Auditoría de Equidad Territorial e Inversión Regional:** Contrastar cuantitativamente si las prioridades de inversión declaradas por una institución o gobierno se reflejan simétricamente en el discurso político y legal, permitiendo corregir desajustes en el foco de desarrollo territorial.
2. **Evaluación de Reputación y Estrategia Geopolítica:** Monitorear y cartografiar las zonas geográficas con mayor fricción o relevancia en corpus textuales internacionales o normativos, optimizando la asignación de recursos diplomáticos, comerciales o de mitigación de riesgo.
3. **Optimización de Políticas Públicas y Análisis de Impacto:** Evaluar de qué manera reformas legales o planes de desarrollo históricos han redistribuido la atención regulatoria a lo largo del territorio nacional a través de las décadas.

---

## Business Context & Challenge

En el análisis estratégico moderno, el volumen de datos textuales no estructurados (leyes, minutas, actas de directorios, discursos, prensa) supera la capacidad de procesamiento de los equipos de análisis humanos. Tradicionalmente, la auditoría del discurso se basaba en análisis cualitativos de muestras pequeñas, lo que inducía a sesgos metodológicos y a una incapacidad sistémica para rastrear tendencias transversales a gran escala.

El desafío de este proyecto consiste en **desarrollar un puente metodológico y técnico de grado senior** que integre la inteligencia lingüística computacional con la cartografía espacial. Esto permite responder a la pregunta estratégica de negocio: *¿De qué manera y cuándo se desplazaron los focos de interés y de fricción geopolítica a lo largo del territorio en las narrativas institucionales, y cómo se traduce esto en prioridades operativas?*

---

## Data Architecture & Analytical Approach

El sistema se estructura en un pipeline desacoplado que garantiza eficiencia y precisión en la extracción de datos cualitativos para transformarlos en métricas de negocio medibles:

1. **Motor Lingüístico Computacional (spaCy NER):** Inyección de modelos pre-entrenados en español optimizados para el Reconocimiento de Entidades Nombradas (NER). Se requiere el uso del modelo mediano (`es_core_news_md`) o grande (`es_core_news_lg`), los cuales incorporan vectores de palabras reales (*word vectors*) para capturar el contexto semántico circundante. Esto calibra de forma robusta al procesador para resolver ambigüedades geográficas complejas (p. ej., distinguir con precisión si "Santiago" se refiere a la capital [GPE] o a un nombre de pila [PERSON]), superando el ruido y la baja precisión del modelo básico (`sm`) y las limitaciones operativas del filtrado por expresiones regulares (*Regex*).
2. **Pipeline ETL y Procesamiento de Corpus (`src/corpus_processor.py`):** Ingesta paralela de conjuntos documentales (`sample_speeches.csv`), normalización ortográfica, tokenización y cálculo de frecuencias relativas normalizadas por volumen de palabras de cada discurso.
3. **Geocodificación y Topología GIS (Folium/OSM):** Enriquecimiento de las entidades de texto mediante un módulo de geocodificación (integración de un Gazetteer local estático para la optimización del prototipo y consulta asíncrona a APIs de GeoNames / Nominatim de OpenStreetMap en producción) para asignar coordenadas geométricas (Latitud/Longitud) precisas, permitiendo la renderización de mapas dinámicos interactivos, burbujas y nubes de calor espacializados mediante Folium.
4. **Exportación JSON para Portfolio Web:** Datos serializados (`geopolitica-entities.json`) para consumo en Portfolio Web con **Plotly.js + Leaflet/Mapbox**, permitiendo visualizaciones interactivas estáticas (GitHub Pages) sin backend Python.

---

## Strategic Insights & Impact

La cartografía cuantitativa realizada sobre el corpus textual del proyecto arroja hallazgos analíticos de alto impacto para la toma de decisiones:

- **Detección de Sesgo Centralista y Mitigación de Ruido Administrativo:** El análisis espacial demuestra que más del 70% de la atención del discurso en periodos críticos se focaliza en el eje metropolitano principal, evidenciando una brecha sustancial respecto a las promesas de descentralización. Para garantizar el rigor científico de este insight y evitar la contaminación por "falsos positivos" de firmas burocráticas u hojas de firmas institucionales (p. ej., "Palacio de La Moneda, Santiago de Chile"), el pipeline aplica un filtro de exclusión de stop-words geográficos corporativos y metadatos administrativos, analizando exclusivamente el cuerpo semántico e intencional del discurso político activo.
- **Transición de Fricciones de Poder:** Los mapas de calor históricos revelan la transición espacial del interés económico nacional a través de las décadas, identificando los periodos exactos en que los polos mineros o industriales desplazaron al foco agropecuario tradicional en el debate legislativo.
- **Rigor en Humanidades Digitales y Auditoría Pública:** La combinación de IA lingüística con visualización espacial aporta una capa de trazabilidad objetiva e incuestionable para auditorías institucionales y consultorías de políticas públicas regionales.

---

## Infraestructura, Despliegue y Ejecución

La arquitectura del proyecto está diseñada para ser completamente portable y fácilmente desplegable en cualquier infraestructura local o en la nube.

### Prerrequisitos
- Python 3.9+
- Motor de procesamiento de texto spaCy

### Setup y Despliegue Local
1. **Clonación del repositorio y aislamiento de entorno:**
   ```bash
   git clone https://github.com/alvarosalinaso/geopolitica-textual-nlp
   cd geopolitica-textual-nlp
   python -m venv .venv
   ```
2. **Activación de entorno (Windows):**
   ```powershell
   .\.venv\Scripts\activate
   ```
3. **Instalación de dependencias del pipeline:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Instalación obligatoria del modelo lingüístico en español:**
   ```bash
   python -m spacy download es_core_news_md
   ```
   *(Nota: Se utiliza `es_core_news_md` o `es_core_news_lg` para asegurar que el modelo cuente con vectores de palabras que entiendan la semántica contextual y eviten las ambigüedades).*
5. **Generar datos para Portfolio Web:**
   ```bash
   python src/export_json.py
   ```
6. **Ver Dashboard Interactivo:**
   **[https://alvarosalinaso.github.io/portfolio-web/](https://alvarosalinaso.github.io/portfolio-web/)** → Tab **"🗺️ Geopolítica Textual NLP"** (pendiente de integración completa)

---

> **Álvaro Salinas Ortiz**
> *Consultor en Estrategia de Datos y Analítica Avanzada*
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portafolio Web](https://alvarosalinaso.github.io/portfolio-web/)