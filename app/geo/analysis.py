import geopandas as gpd


def compute_min_distance_to_settlements(site_geo, settlements_gdf):
    """
    Calculates the minimum distance from the site geometry to any settlement.
    """
    if settlements_gdf.empty:
        return None

    # calculate the distance to all settlements and take the minimum.
    return settlements_gdf.distance(site_geo).min()



def overlaps_any_protected_area(site_geo, protected_areas_gdf):
    """
        Checks if the site intersects with any row in the protected areas GeoDataFrame.
    """
    if protected_areas_gdf.empty:
        return False

    return protected_areas_gdf.intersects(site_geo).any()


def analyze_site(site_gdf: gpd.GeoDataFrame, settlements_gdf: gpd.GeoDataFrame, protected_areas_gdf: gpd.GeoDataFrame) -> dict:
    if site_gdf.empty:
        return {
            "distance_to_settlements_m": None,
            "overlaps_protected_area": False,
        }
    site_geo = site_gdf.union_all()
    distance_to_settlements = compute_min_distance_to_settlements(site_geo, settlements_gdf)
    overlaps_protected_area = overlaps_any_protected_area(site_geo, protected_areas_gdf)

    distance_to_settlements = float(distance_to_settlements)
    overlaps_protected_area = bool(overlaps_protected_area)

    return {
        "distance_to_settlements_m": distance_to_settlements,
        "overlaps_protected_area": overlaps_protected_area,
    }
