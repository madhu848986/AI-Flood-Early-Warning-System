import pandas as pd
from pathlib import Path

input_file = Path(
    "datasets/processed/koshi_pre_event_flood_dataset.csv"
)

output_file = Path(
    "datasets/processed/koshi_pre_event_ml_dataset.csv"
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

ml_df = df[features + [target]].copy()

if ml_df.isnull().any().any():
    raise ValueError("Missing values found.")

ml_df.to_csv(output_file, index=False)

print("PRE-EVENT ML DATASET")
print("--------------------")
print("Records:", len(ml_df))
print("Features:", features)
print("\nLabel distribution:")
print(ml_df[target].value_counts().sort_index())
print("\nMissing values:")
print(ml_df.isnull().sum())
print("\nSaved:", output_file)