import geopandas as gpd
from shapely.geometry import LineString
from shapely.ops import nearest_points
import json

# EPSG:25832 is the standard ETRS89 / UTM zone 32N projection for Germany (meters).
GERMANY_CRS = "EPSG:25832"

# EPSG:4326 is standard WGS 84 Latitude/Longitude required by web maps.
WEB_MAP_CRS = "EPSG:4326"

def _to_web_json(gdf: gpd.GeoDataFrame) -> dict | None:
    """Converts a GeoDataFrame to standard Web Mercator JSON."""
    if gdf.empty:
        return None
    return json.loads(gdf.to_crs(WEB_MAP_CRS).to_json())


def _get_nearest_settlement(site_geo, site_gs: gpd.GeoSeries, settlements_gdf: gpd.GeoDataFrame):
    """Finds the nearest settlement and generates a distance line."""
    if settlements_gdf.empty:
        return None, gpd.GeoDataFrame(crs=GERMANY_CRS), gpd.GeoDataFrame(crs=GERMANY_CRS)


    _, right_idx = settlements_gdf.sindex.nearest(site_gs, return_all=False)
    nearest_settlement = settlements_gdf.iloc[right_idx]

    min_distance = float(nearest_settlement.distance(site_geo).iloc[0])

    # Create connecting line
    nearest_geom = nearest_settlement.geometry.iloc[0]
    pt1, pt2 = nearest_points(site_geo, nearest_geom)
    distance_line_gdf = gpd.GeoDataFrame(geometry=[LineString([pt1, pt2])], crs=GERMANY_CRS)

    return min_distance, nearest_settlement, distance_line_gdf


def _get_protected_area_status(site_geo, site_gs: gpd.GeoSeries, protected_areas_gdf: gpd.GeoDataFrame):
    """Checks for overlapping protected areas, or finds the nearest one."""
    if protected_areas_gdf.empty:
        return False, gpd.GeoDataFrame(crs=GERMANY_CRS)


    intersecting_indices = protected_areas_gdf.sindex.query(site_geo, predicate="intersects")

    if len(intersecting_indices) > 0:
        return True, protected_areas_gdf.iloc[intersecting_indices]


    _, right_idx = protected_areas_gdf.sindex.nearest(site_gs, return_all=False)
    return False, protected_areas_gdf.iloc[right_idx]

def analyze_site(site_gdf: gpd.GeoDataFrame, settlements_gdf: gpd.GeoDataFrame, protected_areas_gdf: gpd.GeoDataFrame) -> dict:
    """Main function to analyze a site against settlements and protected areas."""
    if site_gdf.empty:
        return {"metrics": {}, "map_data": {}}
    site_gdf = site_gdf.to_crs(GERMANY_CRS)
    site_geo = site_gdf.union_all()
    site_gs = gpd.GeoSeries([site_geo], crs=GERMANY_CRS)


    min_distance, nearest_settlement, distance_line = _get_nearest_settlement(
        site_geo, site_gs, settlements_gdf
    )

    overlaps_protected_area, relevant_protected_area = _get_protected_area_status(
        site_geo, site_gs, protected_areas_gdf
    )

    settlement_name = nearest_settlement.iloc[0]["name"] if not nearest_settlement.empty else None
    settlement_type = nearest_settlement.iloc[0]["type"] if not nearest_settlement.empty else None

    if not relevant_protected_area.empty:
        protected_area_names = ", ".join(relevant_protected_area["name"].dropna().astype(str).unique()) or None
        protected_area_types = ", ".join(relevant_protected_area["type"].dropna().astype(str).unique()) or None
    else:
        protected_area_names, protected_area_types = None, None
    return {
        "metrics": {
            "distance_to_settlements_m": min_distance,
            "overlaps_protected_area": overlaps_protected_area,
            "nearest_settlement_name": settlement_name,
            "nearest_settlement_type": settlement_type,
            "protected_area_name": protected_area_names,
            "protected_area_type": protected_area_types,
        },
        "map_data": {
            "site": _to_web_json(site_gdf),
            "nearest_settlement": _to_web_json(nearest_settlement),
            "distance_line": _to_web_json(distance_line),
            "protected_areas": _to_web_json(relevant_protected_area)
        }
    }
