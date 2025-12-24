

from fastapi import APIRouter
from pydantic import BaseModel
from app.geo.parser import load_geodataframe
from app.geo.analysis import analyze_site
from app.rules.engine import evaluate_rules
from app.llm.agent import generate_report
from pathlib import Path
from typing import Dict, Any
import geopandas as gpd
router = APIRouter()
BASE_DIR = Path(__file__).parents[2] / "data"
EXAMPLES_DIR = BASE_DIR / "examples"
PROCESSED_DIR = BASE_DIR / "processed"
TARGET_CRS = "EPSG:25832"

class SiteEvaluationRequest(BaseModel):
    site_geojson: Dict[str, Any]

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/evaluate")
def evaluate_site(payload: SiteEvaluationRequest):
    if payload.site_geojson.get("type") == "FeatureCollection":
        features = payload.site_geojson.get("features")
    elif payload.site_geojson.get("type") == "Feature":
        features = [payload.site_geojson]
    else:
        # Handle raw geometry or other variations if necessary
        features = [{"geometry": payload.site_geojson, "properties": {}}]

    site_gdf = gpd.GeoDataFrame.from_features(features)

    if site_gdf.crs is None:
        site_gdf.set_crs(epsg=4326, inplace=True)

    settlements = load_geodataframe(PROCESSED_DIR / "settlements.gpkg")
    protected_areas = load_geodataframe(PROCESSED_DIR / "protected_areas.gpkg")

    # ensure common CRS
    site_gdf = site_gdf.to_crs(TARGET_CRS)
    settlements = settlements.to_crs(TARGET_CRS)
    protected_areas = protected_areas.to_crs(TARGET_CRS)

    geo_metrics = analyze_site(site_gdf, settlements, protected_areas)
    rule_results = evaluate_rules(geo_metrics)
    report = generate_report(geo_metrics, rule_results)

    return {
        "geo_metrics": geo_metrics,
        "rule_results": rule_results,
        "report": report,
    }
