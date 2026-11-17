import pandas as pd

INPUT_CSV = (
    "datasets/processed/koshi_elevation_zonal_dataset.csv"
)

OUTPUT_CSV = (
    "datasets/processed/koshi_ml_dataset_with_zonal_elevation.csv"
)

df = pd.read_csv(INPUT_CSV)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude",
    "elevation_mean_m"
]

target = "flood_label"

result = df[features + [target]].copy()

result.to_csv(OUTPUT_CSV, index=False)

print("Zonal elevation ML dataset created.")
print("Total records:", len(result))

print("\nMissing values:")
print(result.isna().sum())

print("\nTarget distribution:")
print(result[target].value_counts())

print("\nFeatures:")
print(result.columns.tolist())

print("\nSaved:", OUTPUT_CSV)