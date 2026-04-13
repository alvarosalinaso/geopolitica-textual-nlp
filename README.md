# Geopolítica Textual (NLP): Cartografía de Archivos Históricos

Un proyecto puro enmarcado en las **Humanidades Digitales** y enfoques metodológicos de "Distant Reading". El propósito central de este repositorio es emplear motores de Inteligencia Artificial (Procesamiento de Lenguaje Natural) para evadir las limitaciones de la lectura biológica sobre corpus históricos inmensos.

A través del rastreo de Entidades Nombradas (NER), este pipeline lee automáticamente miles de páginas de discursos gubernamentales o actos jurídicos y extrae, cuenta y geolocaliza qué provincias o territorios figuraron en las narrativas, demostrando el cambio en las fricciones de poder hacia ciertas ciudades a lo largo de los siglos.

---

## Naturaleza Tecnológica (El Híbrido)

El proyecto resuelve un déficit metodológico integrando tres mundos de perfil Senior:

1.  **Motor NLP (Lingüística Computacional):** Las bibliotecas base de `spaCy` corren modelos predictivos ligeros pre-entrenados para reconocer qué sustantivo es una Institución, Persona o Lugar (GPE - Entidades Geopolíticas). Evade la torpeza del *Regex*, ya que la IA sabe por contexto cuándo "Santiago" hace referencia a una plaza geográfica y no a un militar de la colonia con dicho nombre.
2.  **Topología Geográfica (Sistemas de Información Geográfica - GIS):** Módulos como `Folium` y coord-mapping para pasar de simples "números" a la inyección de mapas interactivos HTML.
3.  **Front-End Historiográfico:** Carga inmediata de las métricas de variabilidad en un Dashboard asíncrono para exposición visual, ideal para museos, *papers* académicos interactivos y auditoría municipal.

---

## Despliegue de los Mapas Interactivos

Puedes testear el ecosistema corriendo su modelo de datos local (incluido en `/data`). 

### 1. Instalación de Motor Textual
Este ambiente exige el entrenamiento en español por lo cual las descargas base toman un par de segundos:
```bash
git clone https://github.com/alvarosalinaso/geopolitica-textual-nlp
cd geopolitica-textual-nlp

# Entorno e inyección de requerimientos base
pip install -r requirements.txt

# [NÚCLEO CRÍTICO] Inyección del modelo lingüístico hispano
python -m spacy download es_core_news_sm
```

### 2. Disparo de Interfaz Gráfica
```bash
streamlit run app_mapas.py
```
> El servicio se montará usualmente en el puerto `http://localhost:8501`. Allí podrás renderizar nubes de calor directamente interactuando sobre un globo terráqueo provisto por OpenStreetMaps a través de las abstracciones del script.

---

## Archivos del Dominio

```text
/geopolitica-textual-nlp/
├── app_mapas.py                 # El contenedor de interface (Presentación)
├── src/
│   └── corpus_processor.py      # Core IA/NLP de lectura hermenéutica 
├── data/
│   └── sample_speeches.csv      # Dataset mock (Bypass para test unitario)
```

> **Álvaro Salinas Ortiz** | Arquitectura de Sistemas y Humanidades Digitales
