
from pathlib import Path

import pandas as pd
import pyogrio

RAW_DIR = Path("datasets/raw/osm")
OUTPUT_DIR = RAW_DIR / "koshi"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PBF_FILE = RAW_DIR / "nepal-latest.osm.pbf"

# Study-area bounding box
BBOX = (85.05, 26.05, 88.45, 28.45)

print("Extracting Koshi road network...")

roads = pyogrio.read_dataframe(
    PBF_FILE,
    layer="lines",
    bbox=BBOX
)

roads = roads[
    roads["highway"].notna()
].copy()

roads.to_file(
    OUTPUT_DIR / "koshi_roads.geojson",
    driver="GeoJSON"
)

print("Road features:", len(roads))
print("Road types:")
print(roads["highway"].value_counts().head(15))

print("\nExtracting potential facilities...")

facility_pattern = (
    r'"(amenity|social_facility|emergency)"\s*=>\s*'
    r'"(shelter|hospital|school|community_centre|'
    r'social_facility|clinic|fire_station)"'
)

facility_frames = []

for layer in ["points", "multipolygons"]:

    data = pyogrio.read_dataframe(
        PBF_FILE,
        layer=layer,
        bbox=BBOX
    )

    other_tags = data["other_tags"].fillna("").astype(str)

    match = other_tags.str.contains(
        facility_pattern,
        case=False,
        regex=True
    )

    if "amenity" in data.columns:
        match |= data["amenity"].isin([
            "shelter",
            "hospital",
            "school",
            "community_centre",
            "clinic",
            "fire_station"
        ])

    if "social_facility" in data.columns:
        match |= data["social_facility"].notna()

    if "emergency" in data.columns:
        match |= data["emergency"].notna()

    selected = data[match].copy()
    selected["source_layer"] = layer

    facility_frames.append(selected)

facilities = pd.concat(
    facility_frames,
    ignore_index=True
)

facilities = facilities.drop_duplicates(
    subset=["osm_id", "source_layer"]
)

if not facilities.empty:

    facilities.to_file(
        OUTPUT_DIR / "koshi_potential_facilities.geojson",
        driver="GeoJSON"
    )

print("\nPotential facility records:", len(facilities))

print("\nFacilities by source layer:")
print(facilities["source_layer"].value_counts())

print("\nOSM EXTRACTION COMPLETED")
print("Output folder:", OUTPUT_DIR)
