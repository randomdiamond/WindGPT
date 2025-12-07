from pathlib import Path
import yaml

RULES_PATH = Path(__file__).parent / "config.yaml"


def load_rules() -> dict:
    with RULES_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def evaluate_rules(geo_metrics: dict) -> dict:
    """
    geo_metrics z.B.:
    {
        "distance_to_settlements_m": 500,
        "overlaps_protected_area": False
    }
    """
    rules = load_rules()
    findings = []

    if geo_metrics["distance_to_settlements_m"] < rules["min_distance_to_settlements_m"]:
        findings.append(
            f"Mindestabstand zu Siedlungen ({rules['min_distance_to_settlements_m']} m) nicht erfüllt."
        )

    if rules["no_build_in_protected_area"] and geo_metrics["overlaps_protected_area"]:
        findings.append("Standort liegt in einem Schutzgebiet.")

    return {
        "findings": findings,
        "is_compliant": len(findings) == 0,
    }
