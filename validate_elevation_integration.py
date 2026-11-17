import pandas as pd
import numpy as np

zonal_file = "datasets/processed/koshi_elevation_zonal_dataset.csv"
ml_file = "datasets/processed/koshi_pre_event_ml_with_elevation.csv"
flood_file = "datasets/processed/koshi_pre_event_flood_dataset.csv"

zonal = pd.read_csv(zonal_file)
ml = pd.read_csv(ml_file)
flood = pd.read_csv(flood_file)

print("\nELEVATION INTEGRATION VALIDATION")

print("\n1. DATASET COUNTS")
print("Zonal records:", len(zonal))
print("ML records:", len(ml))
print("Flood records:", len(flood))

print("\n2. MISSING VALUES")
print("Zonal missing:", zonal.isnull().sum().sum())
print("ML missing:", ml.isnull().sum().sum())

print("\n3. DUPLICATE COORDINATES")
print("Zonal duplicates:", zonal.duplicated(
    ["latitude", "longitude"]
).sum())

print("ML duplicates:", ml.duplicated(
    ["latitude", "longitude"]
).sum())

print("\n4. ELEVATION RANGE CHECK")

valid_range = (
    (zonal["elevation_min_m"] <= zonal["elevation_mean_m"])
    & (zonal["elevation_mean_m"] <= zonal["elevation_max_m"])
    & (zonal["elevation_min_m"] <= zonal["elevation_median_m"])
    & (zonal["elevation_median_m"] <= zonal["elevation_max_m"])
)

print("Valid elevation ranges:", valid_range.sum())
print("Invalid elevation ranges:", (~valid_range).sum())

print("\n5. COORDINATE MATCHING")

merged = ml.merge(
    zonal[["latitude", "longitude", "elevation_mean_m"]],
    on=["latitude", "longitude"],
    how="outer",
    suffixes=("_ml", "_zonal"),
    indicator=True
)

print("Both datasets matched:", (merged["_merge"] == "both").sum())
print("Unmatched records:", (merged["_merge"] != "both").sum())

elevation_diff = np.abs(
    merged["elevation_mean_m_ml"]
    - merged["elevation_mean_m_zonal"]
)

print("Exact elevation matches:", (elevation_diff == 0).sum())

print("\n6. FLOOD LABEL MATCHING")

check = ml.merge(
    flood[["latitude", "longitude", "flood_label"]],
    on=["latitude", "longitude"],
    suffixes=("_ml", "_flood"),
    how="outer",
    indicator=True
)

label_matches = (
    (check["_merge"] == "both")
    & (check["flood_label_ml"] == check["flood_label_flood"])
)

print("Matching flood labels:", label_matches.sum())

passed = (
    len(zonal) == 447
    and len(ml) == 447
    and zonal.isnull().sum().sum() == 0
    and ml.isnull().sum().sum() == 0
    and zonal.duplicated(["latitude", "longitude"]).sum() == 0
    and ml.duplicated(["latitude", "longitude"]).sum() == 0
    and valid_range.all()
    and (merged["_merge"] == "both").all()
    and (elevation_diff == 0).all()
    and label_matches.all()
)

print("\nFINAL RESULT:", "PASS" if passed else "CHECK REQUIRED")