import pandas as pd
from pathlib import Path

input_file = Path(
    "datasets/processed/koshi_rainfall_accumulation_october_2021.csv"
)

output_file = Path(
    "datasets/processed/koshi_pre_event_rainfall_oct12.csv"
)

df = pd.read_csv(input_file)

df["date"] = pd.to_datetime(df["date"])

pre_event_date = pd.Timestamp("2021-10-12")

pre_event_df = df[df["date"] == pre_event_date].copy()

required_columns = [
    "latitude",
    "longitude",
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm"
]

pre_event_df = pre_event_df[required_columns]

if pre_event_df.empty:
    raise ValueError("No records found for October 12, 2021.")

if pre_event_df.isnull().any().any():
    raise ValueError("Missing values found in pre-event dataset.")

pre_event_df.to_csv(output_file, index=False)

print("PRE-EVENT RAINFALL DATASET")
print("-------------------------")
print("Records:", len(pre_event_df))
print("Missing values:")
print(pre_event_df.isnull().sum())
print("\nRainfall summary:")
print(pre_event_df.describe())
print("\nSaved:", output_file)