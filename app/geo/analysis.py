
from shapely.geometry import shape
from shapely.ops import nearest_points, unary_union

def compute_min_distance_to_settlements(site_geom, settlements_geojson):
    settlement_geoms = []

    # Collect all settlement geometries
    for feature in settlements_geojson.get("features", []):
        geom = feature.get("geometry")
        if geom is None:
            continue
        settlement_geoms.append(shape(geom))

    if not settlement_geoms:
        return None

    # Merge all settlements into a single geometry for efficient search
    settlements_union = unary_union(settlement_geoms)

    # Find the closest point between site and all settlements
    point_on_site, point_on_settlement = nearest_points(site_geom, settlements_union)


    return point_on_site.distance(point_on_settlement)

def overlaps_any_protected_area(site_geom, protected_areas_geojson):
    for feature in protected_areas_geojson.get("features", []):
        geom = feature.get("geometry")
        if geom is None:
            continue
        protected_geom = shape(geom)

        if site_geom.intersects(protected_geom):
            return True

    return False

def analyze_site(site_geojson: dict, settlements_geojson: dict, protected_areas_geojson: dict) -> dict:

    site_geom = shape(site_geojson["features"][0]["geometry"])


    distance_to_settlements = compute_min_distance_to_settlements(site_geom, settlements_geojson)
    overlaps_protected_area = overlaps_any_protected_area(site_geom, protected_areas_geojson)

    return {
        "distance_to_settlements_m": distance_to_settlements,
        "overlaps_protected_area": overlaps_protected_area,
    }
