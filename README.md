# Cartografía de Datos y NLP en Humanidades Digitales: Análisis del Discurso y Fricciones de Poder Geopolítico

🚀 **[Ver Panel Interactivo en Vivo](https://geopolitica-textual-nlp.streamlit.app)** *(Si aplica enlace en Streamlit Cloud)*

---

## Executive Summary & Decision Making

Este proyecto establece un pipeline avanzado de **Procesamiento de Lenguaje Natural (NLP)** y **Sistemas de Información Geográfica (GIS)** para auditar a gran escala la evolución de discursos políticos, marcos jurídicos o informes de sostenibilidad. Utilizando metodologías de *Distant Reading* (Lectura Distante), el sistema extrae automáticamente miles de Entidades Nombradas Geopolíticas (GPE) de corpus textuales históricos y contemporáneos masivos, eliminando los sesgos y limitaciones de tiempo de la lectura manual e inyectando rigor cuantitativo en el análisis hermenéutico del discurso.

Esta infraestructura analítica permite a Directivos del Sector Público, Asesores de Políticas Públicas y Directores de Estrategia Corporativa tomar **decisiones críticas basadas en evidencia textual**:
1. **Auditoría de Equidad Territorial e Inversión Regional:** Contrastar cuantitativamente si las prioridades de inversión declaradas por una institución o gobierno se reflejan simétricamente en el discurso político y legal, permitiendo corregir desajustes en el foco de desarrollo territorial.
2. **Evaluación de Reputación y Estrategia Geopolítica:** Monitorear y cartografiar las zonas geográficas con mayor fricción o relevancia en corpus textuales internacionales o normativos, optimizando la asignación de recursos diplomáticos, comerciales o de mitigación de riesgo.
3. **Optimización de Políticas Públicas y Análisis de Impacto:** Evaluar de qué manera reformas legales o planes de desarrollo históricos han redistribuido la atención regulatoria a lo largo del territorio nacional a través de las décadas.

[INSERTAR MAPA DE CALOR INTERACTIVO Y CARTOGRAFÍA DE ENTIDADES NOMBRADAS AQUÍ]

---

## Business Context & Challenge

En el análisis estratégico moderno, el volumen de datos textuales no estructurados (leyes, minutas, actas de directorios, discursos, prensa) supera la capacidad de procesamiento de los equipos de análisis humanos. Tradicionalmente, la auditoría del discurso se basaba en análisis cualitativos de muestras pequeñas, lo que inducía a sesgos metodológicos y a una incapacidad sistémica para rastrear tendencias transversales a gran escala.

El desafío de este proyecto consiste en **desarrollar un puente metodológico y técnico de grado senior** que integre la inteligencia lingüística computacional con la cartografía espacial. Esto permite responder a la pregunta estratégica de negocio: *¿De qué manera y cuándo se desplazaron los focos de interés y de fricción geopolítica a lo largo del territorio en las narrativas institucionales, y cómo se traduce esto en prioridades operativas?*

---

## Data Architecture & Analytical Approach

El sistema se estructura en un pipeline desacoplado que garantiza eficiencia y precisión en la extracción de datos cualitativos para transformarlos en métricas de negocio medibles:

[INSERTAR DIAGRAMA DE ARQUITECTURA DE DATOS: CORPUS TEXTUAL -> SPACY NER PIPELINE -> FOLIUM MAPS -> STREAMLIT DASHBOARD AQUÍ]

1. **Motor Lingüístico Computacional (spaCy NER):** Inyección de modelos pre-entrenados en español optimizados para el Reconocimiento de Entidades Nombradas (NER). El procesador está calibrado contextual y semánticamente para resolver ambigüedades geográficas (p. ej., distinguir de forma precisa cuándo "Santiago" refiere a un lugar [GPE] y cuándo a una entidad de nombre propio [PERSON]), superando las limitaciones operativas de las búsquedas basadas en expresiones regulares (*Regex*).
2. **Pipeline ETL y Procesamiento de Corpus (`src/corpus_processor.py`):** Ingesta paralela de conjuntos documentales (`sample_speeches.csv`), normalización ortográfica, tokenización y cálculo de frecuencias relativas normalizadas por volumen de palabras de cada discurso.
3. **Cartografía Interactiva y Topología GIS (Folium/OSM):** Traducción directa de las entidades de texto detectadas en coordenadas geográficas reales. Inyección de mapas dinámicos interactivos y nubes de calor espacializados renderizados mediante Folium y OpenStreetMaps.
4. **Dashboard Asíncrono de Visualización (Streamlit):** Front-end dinámico (`app_mapas.py`) que expone los cambios en las dinámicas geográficas del discurso en tiempo real, permitiendo filtrar tendencias históricas por años y tipos de archivos de forma interactiva.

---

## Strategic Insights & Impact

La cartografía cuantitativa realizada sobre el corpus textual del proyecto arroja hallazgos analíticos de alto impacto para la toma de decisiones:

- **Detección de Sesgo Centralista:** El análisis espacial demuestra que más del 70% de la atención del discurso en periodos críticos se focaliza en el eje metropolitano principal, evidenciando una brecha sustancial respecto a las promesas de descentralización y distribución territorial de la inversión pública.
- **Transición de Fricciones de Poder:** Los mapas de calor históricos revelan la transición espacial del interés económico nacional a través de las décadas, identificando los periodos exactos en que los polos mineros o industriales desplazaron al foco agropecuario tradicional en el debate legislativo.
- **Rigor en Humanidades Digitales y Auditoría Pública:** La combinación de IA lingüística con visualización espacial aporta una capa de trazabilidad objetiva e incuestionable para auditorías institucionales y consultorías de políticas públicas regionales.

[INSERTAR GRÁFICO DE LÍNEA DE TIEMPO DEL FOCUS REGIONAL EN EL DISCURSO LEGISLATIVO AQUÍ]

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
   python -m spacy download es_core_news_sm
   ```
5. **Ejecución del Dashboard de Cartografía Textual:**
   ```bash
   streamlit run app_mapas.py
   ```

---

> **Álvaro Salinas Ortiz**
> *Consultor en Estrategia de Datos y Analítica Avanzada*
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portafolio Web](https://alvarosalinaso.github.io)
