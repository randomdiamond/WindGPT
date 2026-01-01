from pathlib import Path
import warnings

import geopandas as gpd
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
TARGET_CRS = "EPSG:25832"

BKG_DLM250_WFS_URL = "WFS:https://sgx.geodatenzentrum.de/wfs_dlm250?SERVICE=WFS&REQUEST=GetCapabilities"
BFN_SCHUTZGEBIETE_WFS_URL = "https://geodienste.bfn.de/ogc/wfs/schutzgebiet"
PROTECTED_AREAS_OUTPUT_FILE = "protected_areas.gpkg"
SETTLEMENTS_OUTPUT_FILE = "settlements.gpkg"
BKG_NAME_COLS = ["nam"]
BFN_NAME_COLS = ["NAME", "Gebietsname"]
BKG_TYPE_LABEL_COL= "objart_txt"
BKG_SETTLEMENT_LAYERS = [
    "dlm250:objart_31001_p",  # AX_Gebaeude
    "dlm250:objart_41010_f",  # AX_Siedlungsflaeche
    "dlm250:objart_52001_f",  # AX_Ortslage
]

BFN_PROTECTED_AREA_LAYERS = [
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


def fetch_and_process_layers(
        wfs_url: str,
        layers: list[str],
        output_filename: str,
        name_candidates: list[str],
):
    """
    Generic function to download multiple WFS layers, unify columns, and save to GPKG.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / output_filename

    dfs = []
    print(f"Processing {len(layers)} layers for {output_filename}...")

    for layer in layers:
        print(f"  → Fetching {layer} ... ", end="", flush=True)
        try:
            gdf = gpd.read_file(wfs_url, layer=layer, encoding="utf-8")

        except Exception as e:
            print(f"⚠ FAILED: {e}")
            continue


        if gdf.empty:
            print("empty.")
            continue

        if gdf.crs:
            gdf = gdf.to_crs(TARGET_CRS)
        else:
            warnings.warn(f"Layer {layer} has no CRS. Assuming {TARGET_CRS}.")
            gdf = gdf.set_crs(TARGET_CRS)

        gdf["standardized_type"] = layer.split(":")[-1]

        if BKG_TYPE_LABEL_COL in gdf.columns:
            gdf["standardized_type"] = gdf[BKG_TYPE_LABEL_COL].fillna(gdf["standardized_type"])

        dfs.append(gdf)


        print(f"loaded {len(gdf)} features.")

    if not dfs:
        print(f"⚠ No data found for {output_filename}.")
        return

    combined_gdf = pd.concat(dfs, ignore_index=True)



    # Creates a 'standardized_name' column by filling in from the different name_candidates
    combined_gdf["standardized_name"] = None
    existing_name_cols = [c for c in name_candidates if c in combined_gdf.columns]

    for col in existing_name_cols:
        combined_gdf["standardized_name"] = combined_gdf["standardized_name"].fillna(combined_gdf[col])

    final_cols = ["geometry", "standardized_type", "standardized_name"]
    combined_gdf = combined_gdf[final_cols]

    combined_gdf.rename(columns={"standardized_type": "type", "standardized_name": "name"}, inplace=True)



    combined_gdf.to_file(out_path, driver="GPKG", engine="pyogrio")
    print(f"✓ Saved {len(combined_gdf)} features to {out_path}\n")


def main():
    # Process Settlements
    fetch_and_process_layers(
        wfs_url=BKG_DLM250_WFS_URL,
        layers=BKG_SETTLEMENT_LAYERS,
        output_filename=SETTLEMENTS_OUTPUT_FILE,
        name_candidates=BKG_NAME_COLS
    )

    # Process Protected Areas
    fetch_and_process_layers(
        wfs_url=BFN_SCHUTZGEBIETE_WFS_URL,
        layers=BFN_PROTECTED_AREA_LAYERS,
        output_filename=PROTECTED_AREAS_OUTPUT_FILE,
        name_candidates=BFN_NAME_COLS,
    )


if __name__ == "__main__":
    main()