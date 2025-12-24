from pathlib import Path

import geopandas as gpd
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
TARGET_CRS = "EPSG:25832"   # metric system


def preprocess_settlements():
    # 1) Read (Ortslage) polygons
    sie01_path =  RAW_DIR / "dlm250_ebenen" / "sie01_f.shp"
    if sie01_path.exists():
        sie01 = gpd.read_file(sie01_path)
        sie01 = sie01.to_crs(TARGET_CRS)
        print("SIE01 polygons:", len(sie01))

    else:
        sie01 = gpd.GeoDataFrame(geometry=[])

    # 2) Read (Baulich geprägte Flächen) polygons
    sie02_path = RAW_DIR / "dlm250_ebenen" / "sie02_f.shp"
    sie02 = gpd.read_file(sie02_path)
    sie02 = sie02.to_crs(TARGET_CRS)



    # 3) Merge into one GeoDataFrame
    settlements = pd.concat([sie01, sie02], ignore_index=True)

    # Keep only geometry
    keep_cols = ["geometry"]
    for col in ["name", "NAME", "bezeichner"]:
        if col in settlements.columns:
            keep_cols.append(col)
            break

    settlements = settlements[keep_cols]

    # 4) Ensure output folder exists
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 5) Save as GeoPackage
    out_path = PROCESSED_DIR / "settlements.gpkg"
    settlements.to_file(out_path, layer="settlements", driver="GPKG")
    print(f"✓ Saved {len(settlements)} settlement polygons to {out_path}")

def preprocess_protected_areas_simple():
    url = "https://geodienste.bfn.de/ogc/wfs/schutzgebiet"

    # All relevant protected-area layers for wind site evaluation
    layers = [
        "bfn_sch_Schutzgebiet:Nationale_Naturmonumente",
        "bfn_sch_Schutzgebiet:Fauna_Flora_Habitat_Gebiete",
        "bfn_sch_Schutzgebiet:Vogelschutzgebiete",
        "bfn_sch_Schutzgebiet:Biosphaerenreservate",
        "bfn_sch_Schutzgebiet:Biosphaerenreservate_Zonierung",
        "bfn_sch_Schutzgebiet:Nationalparke",
        "bfn_sch_Schutzgebiet:Naturparke",
        "bfn_sch_Schutzgebiet:Naturschutzgebiete",
        "bfn_sch_Schutzgebiet:Landschaftsschutzgebiete",
    ]

    dfs = []

    print("Loading protected areas from BfN WFS (multiple layers)...")
    for layer in layers:
        print(f"  → {layer} ...", end="", flush=True)
        try:
            # Force UTF-8 instead of Windows cp1252
            gdf_layer = gpd.read_file(url, layer=layer, encoding="utf-8")
        except UnicodeDecodeError as e:
            print(f"\n    ⚠ Encoding problem on {layer}: {e}")
            print("    Skipping this layer.")
            continue

        print(f" loaded {len(gdf_layer)} features")

        if gdf_layer.empty:
            continue

        # Ensure CRS and transform
        if gdf_layer.crs is None:
            gdf_layer = gdf_layer.set_crs("EPSG:25832")
        gdf_layer = gdf_layer.to_crs(TARGET_CRS)

        # remember the source layer (useful for filtering/visualisation later)
        gdf_layer["source_layer"] = layer.split(":")[-1]

        dfs.append(gdf_layer)

    if not dfs:
        print("⚠ No protected-area features loaded from any layer.")
        return

    # merge all layers
    gdf = pd.concat(dfs, ignore_index=True)

    print("Merged features from all layers:", len(gdf))

    # keep some useful columns if they exist
    keep_cols = ["geometry", "source_layer"]

    # category / type information
    for c in ["gebietstyp", "SCHUTZKAT", "schutzkategorie", "TYP", "typ"]:
        if c in gdf.columns and c not in keep_cols:
            keep_cols.append(c)

    # names
    for c in ["gebietsname", "NAME", "name"]:
        if c in gdf.columns and c not in keep_cols:
            keep_cols.append(c)

    gdf = gdf[keep_cols]

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "protected_areas.gpkg"
    gdf.to_file(out_path, layer="protected_areas", driver="GPKG")
    print(f"✓ Saved {len(gdf)} protected-area polygons (all layers) to {out_path}")


if __name__ == "__main__":
    preprocess_settlements()
    preprocess_protected_areas_simple()