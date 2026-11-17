
import numpy as np
import pandas as pd
from pathlib import Path

rainfall_path = Path(
    "datasets/processed/"
    "koshi_rainfall_october_13_14_2021.csv"
)

flood_path = Path(
    "datasets/processed/"
    "koshi_nasa_flood_pixels_quality_cs.csv"
)

output_path = Path(
    "datasets/processed/"
    "modis_flood_by_rainfall_cell_cs_quality.csv"
)

rainfall = pd.read_csv(rainfall_path)
flood = pd.read_csv(flood_path)

required_columns = [
    "latitude",
    "longitude",
    "flood_class",
    "valid_observations",
    "total_observations",
    "water_observations",
]

missing = [
    col for col in required_columns
    if col not in flood.columns
]

if missing:
    raise ValueError(f"Missing flood columns: {missing}")

rainfall_cells = (
    rainfall[["latitude", "longitude"]]
    .drop_duplicates()
    .copy()
)

rainfall_cells["latitude"] = rainfall_cells["latitude"].round(6)
rainfall_cells["longitude"] = rainfall_cells["longitude"].round(6)

lat_centers = np.sort(rainfall_cells["latitude"].unique())
lon_centers = np.sort(rainfall_cells["longitude"].unique())

if len(lat_centers) < 2 or len(lon_centers) < 2:
    raise ValueError("Insufficient rainfall grid coordinates.")

lat_step = 0.1
lon_step = 0.1

for col in required_columns:
    flood[col] = pd.to_numeric(flood[col], errors="coerce")

if flood[required_columns].isna().any().any():
    raise ValueError("Missing or invalid values in flood dataset.")

if not flood["flood_class"].isin([0, 1, 2, 3, 255]).all():
    raise ValueError("Unexpected MODIS flood class found.")

flood["latitude"] = np.round(
    lat_centers[0]
    + np.round(
        (flood["latitude"] - lat_centers[0]) / lat_step
    ) * lat_step,
    6,
)

flood["longitude"] = np.round(
    lon_centers[0]
    + np.round(
        (flood["longitude"] - lon_centers[0]) / lon_step
    ) * lon_step,
    6,
)

flood = flood.merge(
    rainfall_cells,
    on=["latitude", "longitude"],
    how="inner",
)

class_counts = (
    flood.groupby(["latitude", "longitude", "flood_class"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=[0, 1, 2, 3, 255], fill_value=0)
)

class_counts.columns = [
    "class_0_count",
    "class_1_count",
    "class_2_count",
    "class_3_count",
    "class_255_count",
]

class_counts["total_pixel_count"] = class_counts.sum(axis=1)

class_counts["classified_pixel_count"] = (
    class_counts[
        [
            "class_0_count",
            "class_1_count",
            "class_2_count",
            "class_3_count",
        ]
    ].sum(axis=1)
)

class_counts["unknown_pixel_count"] = class_counts["class_255_count"]

for class_id in [0, 1, 2, 3, 255]:
    class_counts[f"class_{class_id}_proportion"] = (
        class_counts[f"class_{class_id}_count"]
        / class_counts["total_pixel_count"].replace(0, np.nan)
    )

for class_id in [0, 1, 2, 3]:
    class_counts[f"class_{class_id}_classified_proportion"] = (
        class_counts[f"class_{class_id}_count"]
        / class_counts["classified_pixel_count"].replace(0, np.nan)
    )

quality = (
    flood.groupby(["latitude", "longitude"])
    .agg(
        valid_observations_sum=("valid_observations", "sum"),
        valid_observations_mean=("valid_observations", "mean"),
        total_observations_sum=("total_observations", "sum"),
        total_observations_mean=("total_observations", "mean"),
        water_observations_sum=("water_observations", "sum"),
        water_observations_mean=("water_observations", "mean"),
    )
)

result = rainfall_cells.merge(
    class_counts.reset_index(),
    on=["latitude", "longitude"],
    how="left",
)

result = result.merge(
    quality.reset_index(),
    on=["latitude", "longitude"],
    how="left",
)

count_columns = [
    "class_0_count",
    "class_1_count",
    "class_2_count",
    "class_3_count",
    "class_255_count",
    "total_pixel_count",
    "classified_pixel_count",
    "unknown_pixel_count",
    "valid_observations_sum",
    "total_observations_sum",
    "water_observations_sum",
]

result[count_columns] = (
    result[count_columns].fillna(0).astype(int)
)

result.to_csv(output_path, index=False)

print("CLOUD-SHADOW-CORRECTED MODIS AGGREGATION")
print("=" * 55)

print("Rainfall grid cells:", len(rainfall_cells))
print("Aggregated cells:", len(result))
print("MODIS pixels in overlap:", len(flood))

print(
    "Cells with classified MODIS pixels:",
    (result["classified_pixel_count"] > 0).sum()
)

print(
    "Cells with unknown MODIS pixels:",
    (result["unknown_pixel_count"] > 0).sum()
)

print("\nTotal flood-class pixels:")
for class_id in [0, 1, 2, 3, 255]:
    print(
        f"Class {class_id}:",
        result[f"class_{class_id}_count"].sum()
    )

print("\nOutput:", output_path)

print("\nFirst 10 rows:")
print(result.head(10).to_string(index=False))
