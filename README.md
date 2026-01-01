# 🛰️ WindGPT
> **Automated Site Assessment & Constraint Analysis.**
> Rapidly evaluates location feasibility by combining geospatial processing with AI-generated reporting.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Geo](https://img.shields.io/badge/Geo-Shapely%20%7C%20GeoPandas-yellow)
![AI](https://img.shields.io/badge/AI-OpenAI%20API-green)
![Status](https://img.shields.io/badge/Status-Learning%20Project-purple)

---

## ⚡ Overview

**WindGPT** is a Python-based tool designed to automate the initial "sanity check" for potential wind farm locations.

Instead of manual map measurements, the tool processes a target location (GeoJSON) through a three-step pipeline:

1. **Settlement Proximity (DLM250):**  
   Calculates precise distances to nearby buildings to verify regional buffer zones (e.g., 1000m rules).

2. **Environmental Constraints (BfN):**  
   Detects intersections with official protected areas to identify zoning risks immediately.

3. **AI Assessment:**  
   Synthesizes these spatial findings via the ChatGPT API into a structured architectural feasibility report.
