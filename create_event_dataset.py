
import pandas as pd
from pathlib import Path

rainfall_file = Path(
    "datasets/processed/"
    "koshi_rainfall_accumulation_october_2021.csv"
)

flood_file = Path(
    "datasets/processed/"
    "koshi_modis_flood_cell_summary.csv"
)

output_file = Path(
    "datasets/processed/"
    "koshi_event_analysis_dataset.csv"
)

rainfall = pd.read_csv(rainfall_file)
flood = pd.read_csv(flood_file)
rainfall["latitude"] = rainfall["latitude"].round(2)
rainfall["longitude"] = rainfall["longitude"].round(2)

flood["latitude"] = flood["latitude"].round(2)
flood["longitude"] = flood["longitude"].round(2)

rainfall["date"] = pd.to_datetime(rainfall["date"])

event_rainfall = rainfall[
    rainfall["date"] == "2021-10-13"
].copy()

event_rainfall = event_rainfall.drop(
    columns=["date"]
)

dataset = pd.merge(
    event_rainfall,
    flood,
    on=["latitude", "longitude"],
    how="inner",
    validate="one_to_one"
)

dataset["flood_label"] = (
    dataset["flood_pixels"] > 0
).astype(int)

dataset = dataset.sort_values(
    ["latitude", "longitude"]
).reset_index(drop=True)

dataset.to_csv(output_file, index=False)

print("EVENT ANALYSIS DATASET")
print("=" * 45)

print("Total records:", len(dataset))
print("Unique grid cells:", dataset[
    ["latitude", "longitude"]
].drop_duplicates().shape[0])

print("\nFlood label distribution:")
print(dataset["flood_label"].value_counts())

print("\nMissing values:")
print(dataset.isnull().sum())

print("\nDataset columns:")
print(dataset.columns.tolist())

print("\nSample records:")
print(dataset.head().to_string(index=False))

print("\nSaved to:", output_file)
