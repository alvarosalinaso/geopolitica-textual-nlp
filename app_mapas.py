import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from src.corpus_processor import GeopoliticalExtractor

# Diccionario de Geocodificación Estática para el demostrador (Evita bloqueos de API externas)
# En producción, se enlazará a GeoPandas + OpenStreetMap API (Nominatim)
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
    "Biobío": [-37.4667, -72.3500] 
}

st.set_page_config(page_title="Cartografía Textual Histórica", layout="wide", page_icon="🗺️")

st.title("🗺️ Geopolítica Textual: Mapas HD")
st.markdown("Plataforma interactiva de **Distant Reading**. Descubre qué territorios acaparan el foco político leyendo automáticamente cientos de actas de gobierno con IA.")

@st.cache_data
def load_and_extract_data():
    dataset_path = os.path.join("data", "sample_speeches.csv")
    extractor = GeopoliticalExtractor(model_size="es_core_news_md")
    results = extractor.process_corpus(dataset_path)
    return results

with st.spinner("Motor NLP Leyendo Corpus. Por favor espere..."):
    df_places = load_and_extract_data()

if df_places.empty:
    st.error("No se pudo iniciar el modelo NLP. Asegúrate de haber instalado 'es_core_news_sm'.")
    st.info("Comando de terminal: python -m spacy download es_core_news_sm")
else:
    # Preparación de datos georeferenciados
    df_places['Coords'] = df_places['Mentioned_Location'].map(GEO_DB)
    df_validos = df_places.dropna(subset=['Coords'])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Frecuencia Territorial")
        st.dataframe(df_validos['Mentioned_Location'].value_counts().reset_index(name='Menciones'), use_container_width=True)
        st.markdown("### Filtro de Época")
        years = df_validos['Year'].unique()
        selected_years = st.multiselect("Seleccionar Siglo / Década", sorted(years), default=sorted(years))
    
    with col2:
        st.subheader("📍 Cartografía de Poder")
        
        # Filtrar DF para el mapa
        df_mapa = df_validos[df_validos['Year'].isin(selected_years)]
        
        # Iniciar Folium centrado en Chile
        m = folium.Map(location=[-35.6, -71.5], zoom_start=4, tiles="CartoDB positron")
        
        # Compresión de conteos para burbujas
        freq_coords = df_mapa['Mentioned_Location'].value_counts().to_dict()
        
        for location, count in freq_coords.items():
            coords = GEO_DB[location]
            # Burbujar proporcional a menciones
            folium.CircleMarker(
                location=coords,
                radius=10 + (count * 5),
                popup=f"{location}: {count} menciones",
                color="#0068c9",
                fill=True,
                fill_color="#0068c9",
                fill_opacity=0.7
            ).add_to(m)
            
        st_data = st_folium(m, width=700, height=500)
    
    st.divider()
    st.caption("Arquitectura NLP base (spaCy) · Motor Gráfico: Folium / OpenStreetMaps · Proyecto de Humanidades Digitales")
