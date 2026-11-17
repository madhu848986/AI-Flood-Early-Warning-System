import pandas as pd
import numpy as np

file = "datasets/processed/koshi_pre_event_flood_dataset.csv"

df = pd.read_csv(file)

print("\nMODIS FLOOD LABEL VALIDATION")

print("\n1. DATASET INFORMATION")
print("Total cells:", len(df))
print("Missing values:", df.isnull().sum().sum())
print("Duplicate coordinates:", df.duplicated(
    subset=["latitude", "longitude"]
).sum())

print("\n2. FLOOD LABEL DISTRIBUTION")
print(df["flood_label"].value_counts().sort_index())

print("\n3. FLOOD LABEL CHECK")

expected = (df["flood_pixels"] > 0).astype(int)

print("Correct labels:", (expected == df["flood_label"]).sum())
print("Incorrect labels:", (expected != df["flood_label"]).sum())

print("\n4. PIXEL COUNT VALIDATION")

pixel_sum = (
    df["no_water_pixels"]
    + df["reference_water_pixels"]
    + df["recurring_flood_pixels"]
    + df["flood_pixels"]
)

print("Correct pixel totals:", (pixel_sum == df["valid_pixels"]).sum())
print("Incorrect pixel totals:", (pixel_sum != df["valid_pixels"]).sum())

print("\n5. FLOOD RATIO VALIDATION")

expected_ratio = df["flood_pixels"] / df["valid_pixels"]

ratio_diff = np.abs(
    expected_ratio - df["flood_pixel_ratio"]
)

print("Exact ratio matches:", (ratio_diff < 1e-10).sum())
print("Maximum ratio difference:", ratio_diff.max())

print("\n6. FINAL RESULT")

passed = (
    df.isnull().sum().sum() == 0
    and df.duplicated(
        subset=["latitude", "longitude"]
    ).sum() == 0
    and (expected == df["flood_label"]).all()
    and (pixel_sum == df["valid_pixels"]).all()
    and (ratio_diff < 1e-10).all()
)

print("RESULT:", "PASS" if passed else "CHECK REQUIRED")