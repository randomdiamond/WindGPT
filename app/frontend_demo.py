import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.title("WindGPT Demo")

site_file = st.text_input("Site-Datei", "site.geojson")

if st.button("Standort bewerten"):
    resp = requests.post(
        f"{BACKEND_URL}/api/evaluate",
        json={"site_file": site_file},
        timeout=60,
    )
    data = resp.json()
    st.subheader("Bericht")
    st.write(data["report"])
    st.subheader("Geo-Metriken")
    st.json(data["geo_metrics"])
    st.subheader("Regel-Check")
    st.json(data["rule_results"])