import pandas as pd

INPUT_FILE = (
    "datasets/processed/koshi_elevation_dataset.csv"
)

OUTPUT_FILE = (
    "datasets/processed/koshi_ml_dataset_with_elevation.csv"
)

df = pd.read_csv(INPUT_FILE)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude",
    "elevation_m"
]

target = "flood_label"

ml_df = df[features + [target]].copy()

ml_df.to_csv(OUTPUT_FILE, index=False)

print("Elevation-enhanced ML dataset created.")
print("Total records:", len(ml_df))
print("\nFeatures:")
print(features)

print("\nMissing values:")
print(ml_df.isnull().sum())

print("\nFlood label distribution:")
print(ml_df[target].value_counts())

print("\nSaved at:", OUTPUT_FILE)