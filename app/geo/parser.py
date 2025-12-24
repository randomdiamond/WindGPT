
from pathlib import Path
import json
import geopandas as gpd

def load_geojson(path: str | Path) -> dict:
    """Loads a filepath into a geojson dictionary."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def load_geodataframe(path: str | Path):
    """Loads a file (GeoJSON or GPKG) into a GeoPandas DataFrame"""
    return gpd.read_file(path)