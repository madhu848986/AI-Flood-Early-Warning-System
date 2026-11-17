import pandas as pd

INPUT_CSV = (
    "datasets/processed/koshi_elevation_zonal_dataset.csv"
)

OUTPUT_CSV = (
    "datasets/processed/koshi_ml_dataset_with_terrain_range.csv"
)

df = pd.read_csv(INPUT_CSV)

df["elevation_range_m"] = (
    df["elevation_max_m"] - df["elevation_min_m"]
)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude",
    "elevation_mean_m",
    "elevation_range_m"
]

result = df[features + ["flood_label"]].copy()

result.to_csv(OUTPUT_CSV, index=False)

print("Terrain range dataset created.")
print("Total records:", len(result))

print("\nMissing values:")
print(result.isna().sum())

print("\nElevation range summary:")
print(result["elevation_range_m"].describe().round(2))

print("\nSaved:", OUTPUT_CSV)