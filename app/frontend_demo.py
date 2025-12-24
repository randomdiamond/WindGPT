import streamlit as st
import requests
import json
BACKEND_URL = "http://localhost:8000"


uploaded_file = st.file_uploader("Standortdatei (GeoJSON)", type=["geojson"])

if st.button("Standort bewerten"):
    if uploaded_file is not None:
        try:
            geojson_data = json.load(uploaded_file)
            payload = {
                "site_geojson": geojson_data
            }
            with st.spinner("Analysiere Geometrie"):
                resp = requests.post(
                    f"{BACKEND_URL}/api/evaluate",
                    json=payload,
                    timeout=60,
                )git

            if resp.status_code == 200:
                data = resp.json()

                st.success("Analyse Fertig")

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
