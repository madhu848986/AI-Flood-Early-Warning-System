
from pathlib import Path

import pandas as pd
import pyogrio

RAW_DIR = Path("datasets/raw/osm")
OUTPUT_DIR = RAW_DIR / "koshi"

PBF_FILE = RAW_DIR / "nepal-latest.osm.pbf"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BBOX = (85.05, 26.05, 88.45, 28.45)

COLUMNS = [
    "osm_id",
    "name",
    "amenity",
    "other_tags",
    "social_facility",
    "emergency"
]

facility_frames = []

for layer in ["points", "multipolygons"]:

    print(f"\nReading {layer}...")

    info = pyogrio.read_info(PBF_FILE, layer=layer)
    available = set(info["fields"])

    columns = [
        column for column in COLUMNS
        if column in available
    ]

    data = pyogrio.read_dataframe(
        PBF_FILE,
        layer=layer,
        bbox=BBOX,
        columns=columns
    )

    mask = pd.Series(False, index=data.index)

    if "amenity" in data.columns:
        mask |= data["amenity"].isin([
            "shelter",
            "hospital",
            "school",
            "community_centre",
            "clinic",
            "fire_station"
        ])

    if "social_facility" in data.columns:
        mask |= data["social_facility"].notna()

    if "emergency" in data.columns:
        mask |= data["emergency"].notna()

    if "other_tags" in data.columns:
        tags = data["other_tags"].fillna("").astype(str)

        pattern = (
            r'"(?:amenity|social_facility|emergency)"\s*=>\s*'
            r'"(?:shelter|hospital|school|community_centre|'
            r'clinic|fire_station)"'
        )

        mask |= tags.str.contains(pattern, case=False, regex=True)

    selected = data.loc[mask].copy()
    selected["source_layer"] = layer

    facility_frames.append(selected)

    print("Matching features:", len(selected))

    del data
    del selected

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

    facilities.drop(columns="geometry").to_csv(
        OUTPUT_DIR / "koshi_potential_facilities.csv",
        index=False
    )

print("\nFACILITY EXTRACTION COMPLETED")
print("Total potential facilities:", len(facilities))
print("\nFacilities by layer:")
print(facilities["source_layer"].value_counts())
print("\nSaved in:", OUTPUT_DIR)
