
import pandas as pd
from pathlib import Path

input_file = Path(
    "datasets/processed/koshi_event_analysis_dataset.csv"
)

output_file = Path(
    "datasets/processed/koshi_ml_dataset.csv"
)

df = pd.read_csv(input_file)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude"
]

target = "flood_label"

model_df = df[features + [target]].copy()

print("ML DATASET PREPARATION")
print("=" * 40)

print("Total records:", len(model_df))
print("\nFeatures:")
print(features)

print("\nTarget distribution:")
print(model_df[target].value_counts())

print("\nMissing values:")
print(model_df.isnull().sum())

print("\nClass distribution percentage:")
print(
    (model_df[target].value_counts(normalize=True) * 100).round(2)
)

model_df.to_csv(output_file, index=False)

print("\nSaved:", output_file)
