from pathlib import Path
import pandas as pd

rainfall_file = Path(
    "datasets/processed/koshi_pre_event_rainfall_oct12.csv"
)

modis_file = Path(
    "datasets/processed/koshi_modis_flood_cell_summary.csv"
)

output_file = Path(
    "datasets/processed/koshi_pre_event_flood_dataset.csv"
)

rainfall = pd.read_csv(rainfall_file)
modis = pd.read_csv(modis_file)

print("MODIS columns:")
print(modis.columns.tolist())

required_modis_columns = [
    "latitude",
    "longitude",
    "flood_pixels"
]

for column in required_modis_columns:
    if column not in modis.columns:
        raise ValueError(f"Required MODIS column missing: {column}")

rainfall["latitude"] = rainfall["latitude"].round(2)
rainfall["longitude"] = rainfall["longitude"].round(2)

modis["latitude"] = modis["latitude"].round(2)
modis["longitude"] = modis["longitude"].round(2)

if rainfall.duplicated(["latitude", "longitude"]).any():
    raise ValueError("Duplicate rainfall grid cells found.")

if modis.duplicated(["latitude", "longitude"]).any():
    raise ValueError("Duplicate MODIS grid cells found.")

merged = pd.merge(
    rainfall,
    modis,
    on=["latitude", "longitude"],
    how="inner",
    validate="one_to_one"
)

merged["flood_label"] = (
    merged["flood_pixels"] > 0
).astype(int)

if merged.empty:
    raise ValueError("No matching grid cells found.")

if merged.isnull().any().any():
    print("\nMissing values:")
    print(merged.isnull().sum())
    raise ValueError("Missing values found in merged dataset.")

merged.to_csv(output_file, index=False)

print("\nPRE-EVENT FLOOD DATASET")
print("----------------------")
print("Rainfall grid cells:", len(rainfall))
print("MODIS grid cells:", len(modis))
print("Matched grid cells:", len(merged))

print("\nFlood label distribution:")
print(merged["flood_label"].value_counts().sort_index())

print("\nMissing values:")
print(merged.isnull().sum())

print("\nSaved:", output_file)