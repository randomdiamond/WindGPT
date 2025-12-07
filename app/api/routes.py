

from fastapi import APIRouter
from pydantic import BaseModel
from app.geo.parser import load_geojson
from app.geo.analysis import analyze_site
from app.rules.engine import evaluate_rules
from app.llm.agent import generate_report
from pathlib import Path
router = APIRouter()
DATA_DIR = Path(__file__).parents[2] / "data" / "examples"


class SiteEvaluationRequest(BaseModel):
    site_file: str

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/evaluate")
def evaluate_site(payload: SiteEvaluationRequest):
    site = load_geojson(DATA_DIR / payload.site_file)
    settlements = load_geojson(DATA_DIR / "settlements.geojson")
    protected_areas = load_geojson(DATA_DIR / "protected_areas.geojson")

    geo_metrics = analyze_site(site, settlements, protected_areas)
    rule_results = evaluate_rules(geo_metrics)
    report = generate_report(geo_metrics, rule_results)

    return {
        "geo_metrics": geo_metrics,
        "rule_results": rule_results,
        "report": report,
    }
