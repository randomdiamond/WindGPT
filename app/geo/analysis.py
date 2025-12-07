
from shapely.geometry import shape
from shapely.ops import nearest_points

def compute_min_distance_to_settlements(site_geom, settlements):
    # TODO: echte Implementierung
    return 500

def analyze_site(site_geojson: dict, settlements_geojson: dict, protected_areas_geojson: dict) -> dict:
    # TODO: GeoJSON -> shapely Geometry
    site_geom = shape(site_geojson["features"][0]["geometry"])
    # Dummy:
    distance_to_settlements = 500
    overlaps_protected_area = False

    return {
        "distance_to_settlements_m": distance_to_settlements,
        "overlaps_protected_area": overlaps_protected_area,
    }
