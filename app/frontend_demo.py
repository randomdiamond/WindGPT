import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
BACKEND_URL = "http://localhost:8000"


def create_folium_map(map_data, metrics):
    """Generates a Folium map with styled GeoJSON layers and dynamic zoom."""
    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6)
    all_bounds = []

    # Protected Areas
    if map_data.get("protected_areas"):
        pa_layer = folium.GeoJson(
            map_data["protected_areas"],
            name="Schutzgebiete (BfN)",
            style_function=lambda feature: {
                "fillColor": "#2ca02c",
                "color": "#2ca02c",
                "weight": 2,
                "fillOpacity": 0.4,
            },
            tooltip=folium.GeoJsonTooltip(fields=["name", "type"]) if "name" in str(
                map_data["protected_areas"]) else None
        )
        pa_layer.add_to(m)
        all_bounds.extend(pa_layer.get_bounds())

    # Nearest Settlement
    if map_data.get("nearest_settlement"):
        settlement_layer = folium.GeoJson(
            map_data["nearest_settlement"],
            name="Nächste Siedlung",
            style_function=lambda feature: {
                "fillColor": "#ff7f0e",
                "color": "#ff7f0e",
                "weight": 2,
                "fillOpacity": 0.6,
            },
            tooltip=folium.GeoJsonTooltip(fields=["name", "type"]) if "name" in str(
                map_data["nearest_settlement"]) else None
        )
        settlement_layer.add_to(m)
        all_bounds.extend(settlement_layer.get_bounds())

    # Distance Line and Midpoint Text Label
    if map_data.get("distance_line"):

        distance_layer = folium.GeoJson(
            map_data["distance_line"],
            name="Abstand zur Siedlung",
            style_function=lambda feature: {
                "color": "#d62728",
                "weight": 3,
                "dashArray": "5, 5",
            }
        )
        distance_layer.add_to(m)
        all_bounds.extend(distance_layer.get_bounds())


        features = map_data["distance_line"].get("features", [])
        if features:
            coords = features[0].get("geometry", {}).get("coordinates", [])

            if len(coords) == 2:
                lon1, lat1 = coords[0]
                lon2, lat2 = coords[1]

                mid_lat = (lat1 + lat2) / 2
                mid_lon = (lon1 + lon2) / 2

                dist_m = metrics.get("distance_to_settlements_m", 0)
                formatted_dist = f"{dist_m:.1f} m"

                # Place a DivIcon at the midpoint
                folium.Marker(
                    location=[mid_lat, mid_lon],
                    icon=folium.DivIcon(
                        icon_size=(100, 20),
                        icon_anchor=(50, 10),  # Center the text block over the line
                        html=f'''
                            <div style="
                                font-size: 13px; 
                                font-weight: bold; 
                                color: #d62728; 
                                background-color: rgba(255, 255, 255, 0.85); 
                                border: 1px solid #d62728;
                                border-radius: 4px;
                                padding: 2px 5px;
                                white-space: nowrap;
                                text-align: center;
                                display: inline-block;
                            ">
                                {formatted_dist}
                            </div>
                        '''
                    )
                ).add_to(m)

    # Target Site
    if map_data.get("site"):
        site_layer = folium.GeoJson(
            map_data["site"],
            name="Geplanter Standort",
            style_function=lambda feature: {
                "fillColor": "#1f77b4",
                "color": "#1f77b4",
                "weight": 3,
                "fillOpacity": 0.7,
            }
        )
        site_layer.add_to(m)
        all_bounds.extend(site_layer.get_bounds())


    if all_bounds:
        min_lat = min(b[0] for b in all_bounds)
        min_lon = min(b[1] for b in all_bounds)
        max_lat = max(b[0] for b in all_bounds)
        max_lon = max(b[1] for b in all_bounds)
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    folium.LayerControl().add_to(m)

    return m


st.title("WindGPT - Standortprüfung")
uploaded_file = st.file_uploader("Standortdatei (GeoJSON)", type=["geojson"])

if st.button("Standort bewerten"):
    if uploaded_file is not None:
        try:
            geojson_data = json.load(uploaded_file)
            payload = {
                "site_geojson": geojson_data
            }
            with st.spinner("Analysiere Standort"):
                resp = requests.post(
                    f"{BACKEND_URL}/api/evaluate",
                    json=payload,
                    timeout=60,
                )

            if resp.status_code == 200:
                data = resp.json()

                st.success("Analyse Fertig")
                st.subheader("Kartographische Übersicht")
                if "map_data" in data and "geo_metrics" in data:
                    wind_map = create_folium_map(data["map_data"], data["geo_metrics"])
                    st_folium(wind_map, width=700, height=500, returned_objects=[])
                else:
                    st.warning("Keine Kartendaten vom Backend empfangen.")

                st.subheader("Bericht")
                st.write(data["report"])

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Geo-Metriken")
                    st.json(data["geo_metrics"])
                with col2:
                    st.subheader("Regel-Check")
                    st.json(data["rule_results"])
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")

        except json.JSONDecodeError:
            st.error("Invalid JSON file uploaded.")
    else:
        st.warning("Please upload a GeoJSON file first.")
