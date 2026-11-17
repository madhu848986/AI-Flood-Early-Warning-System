import pandas as pd
from pathlib import Path

rainfall_file = Path(
    "datasets/processed/koshi_pre_event_flood_dataset.csv"
)

elevation_file = Path(
    "datasets/processed/koshi_elevation_zonal_dataset.csv"
)

output_file = Path(
    "datasets/processed/koshi_pre_event_ml_with_elevation.csv"
)

rainfall = pd.read_csv(rainfall_file)
elevation = pd.read_csv(elevation_file)

rainfall["latitude"] = rainfall["latitude"].round(2)
rainfall["longitude"] = rainfall["longitude"].round(2)

elevation["latitude"] = elevation["latitude"].round(2)
elevation["longitude"] = elevation["longitude"].round(2)

merged = pd.merge(
    rainfall,
    elevation[
        [
            "latitude",
            "longitude",
            "elevation_mean_m"
        ]
    ],
    on=["latitude", "longitude"],
    how="inner",
    validate="one_to_one"
)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude",
    "elevation_mean_m"
]

output = merged[features + ["flood_label"]].copy()

if len(output) != len(rainfall):
    raise ValueError("Some rainfall grid cells did not match elevation data.")

if output.isnull().any().any():
    raise ValueError("Missing values found.")

output.to_csv(output_file, index=False)

print("PRE-EVENT DATASET WITH ELEVATION")
print("--------------------------------")
print("Records:", len(output))
print("Features:", features)
print("\nLabel distribution:")
print(output["flood_label"].value_counts().sort_index())
print("\nMissing values:")
print(output.isnull().sum())
print("\nSaved:", output_file)