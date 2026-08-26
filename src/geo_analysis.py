"""
Análisis geoespacial con Folium — Mapa interactivo de entidades geopolíticas.
"""

import json
from pathlib import Path

try:
    import folium
    from folium.plugins import HeatMap, MarkerCluster

    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# Coordenadas de ciudades/entidades chilenas y geopolíticas
ENTITY_COORDS = {
    "Santiago": (-33.4489, -70.6693),
    "Valparaíso": (-33.0472, -71.6127),
    "Concepción": (-36.8270, -73.0503),
    "Chile": (-35.6751, -71.5430),
    "Argentina": (-38.4161, -63.6167),
    "Brasil": (-14.2350, -51.9253),
    "Perú": (-9.1900, -75.0152),
    "Bolivia": (-16.2902, -63.5887),
    "Colombia": (4.5709, -74.2973),
    "EEUU": (37.0902, -95.7129),
    "China": (35.8617, 104.1954),
    "Rusia": (61.5240, 105.3188),
    "Unión Europea": (50.1109, 8.6821),
    "Cuba": (21.5218, -77.7812),
    "Venezuela": (6.4238, -66.5897),
    "México": (23.6345, -102.5528),
}


def run_geo_analysis(
    data_dir: Path = Path("data/export"), output_dir: Path = Path("data/export")
) -> dict:
    """
    Genera mapa interactivo Folium de entidades geopolíticas.

    Returns:
        dict con estadísticas y path del mapa
    """
    if not FOLIUM_AVAILABLE:
        print("[GEO] folium no instalado. pip install folium")
        return {}

    # Load NER data
    ner_file = data_dir / "ner_entities.json"
    if not ner_file.exists():
        print(
            "[GEO] ner_entities.json no encontrado — ejecutar ner_analysis.py primero"
        )
        return {}

    with open(ner_file, encoding="utf-8") as f:
        data = json.load(f)

    entities = data.get("top_entities", [])

    # Create map centered on Chile
    m = folium.Map(
        location=[-33.4489, -70.6693], zoom_start=3, tiles="CartoDB dark_matter"
    )

    # Add markers for each entity
    marker_cluster = MarkerCluster().add_to(m)
    entities_plotted = 0

    for ent in entities:
        name = ent["entity"]
        # Try exact match, then partial
        coords = ENTITY_COORDS.get(name)
        if not coords:
            for key, value in ENTITY_COORDS.items():
                if key.lower() in name.lower() or name.lower() in key.lower():
                    coords = value
                    break

        if coords:
            folium.Marker(
                location=coords,
                popup=folium.Popup(
                    f"<b>{name}</b><br>Tipo: {ent['label']}<br>Frecuencia: {ent['count']}",
                    max_width=200,
                ),
                tooltip=name,
                icon=folium.Icon(
                    color="red"
                    if ent["count"] > 100
                    else "orange"
                    if ent["count"] > 50
                    else "blue",
                    icon="info-sign",
                ),
            ).add_to(marker_cluster)
            entities_plotted += 1

    # Add heatmap layer
    heat_data = []
    for ent in entities:
        name = ent["entity"]
        coords = ENTITY_COORDS.get(name)
        if not coords:
            for key, value in ENTITY_COORDS.items():
                if key.lower() in name.lower():
                    coords = value
                    break
        if coords:
            heat_data.append([coords[0], coords[1], ent["count"]])

    if heat_data:
        HeatMap(heat_data, radius=25, blur=15, max_zoom=1).add_to(m)

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    map_file = output_dir / "geopolitical_map.html"
    m.save(str(map_file))

    results = {
        "entities_plotted": entities_plotted,
        "total_entities": len(entities),
        "map_file": str(map_file),
        "unique_locations": len(
            {
                e["entity"]
                for e in entities
                if any(k.lower() in e["entity"].lower() for k in ENTITY_COORDS)
            }
        ),
    }

    print(f"[GEO] Mapa generado: {map_file}")
    print(f"[GEO] {entities_plotted} entidades plotteadas de {len(entities)} totales")
    return results


if __name__ == "__main__":
    run_geo_analysis()
