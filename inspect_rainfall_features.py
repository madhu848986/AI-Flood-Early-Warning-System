
from pathlib import Path

import pandas as pd

file_path = Path(
    "datasets/processed/koshi_pre_event_ml_dataset.csv"
)

df = pd.read_csv(file_path)

rainfall_columns = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm"
]

print("RAINFALL FEATURE INSPECTION")
print("---------------------------")

print("\nDataset shape:", df.shape)

print("\nMissing values:")
print(df[rainfall_columns].isnull().sum())

print("\nZero-value counts:")
print((df[rainfall_columns] == 0).sum())

print("\nOverall rainfall statistics:")
print(df[rainfall_columns].describe().round(4))

print("\nRainfall statistics by flood label:")
print(
    df.groupby("flood_label")[rainfall_columns]
    .agg(["mean", "median", "std", "min", "max"])
    .round(4)
)

print("\nFlood label counts:")
print(df["flood_label"].value_counts())
