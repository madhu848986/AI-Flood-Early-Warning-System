import pandas as pd

input_path = (
    "datasets/processed/koshi_rainfall_flood_integrated.csv"
)

output_path = (
    "datasets/processed/koshi_model_analysis.csv"
)

df = pd.read_csv(input_path)

# Keep only records with valid MODIS observations
df = df[df["flood_observation_available"] == True].copy()

# Retain rainfall, coordinates, flood observations, and label
columns = [
    "date",
    "latitude",
    "longitude",
    "precipitation_mm_per_day",
    "valid_pixels",
    "no_water_pixels",
    "reference_water_pixels",
    "recurring_flood_pixels",
    "flood_pixels",
    "flood_pixel_ratio",
    "recurring_or_flood_ratio",
    "observed_flood_present",
]

analysis = df[columns].copy()

analysis.to_csv(output_path, index=False)

print("MODEL ANALYSIS DATASET")
print("=" * 45)
print("Total records:", len(analysis))
print("Unique grid cells:",
      analysis[["latitude", "longitude"]].drop_duplicates().shape[0])

print("\nRecords by date:")
print(analysis.groupby("date").size())

print("\nProvisional observed-flood label counts:")
print(analysis["observed_flood_present"].value_counts())

print("\nMissing values:")
print(analysis.isna().sum())

print("\nOutput saved to:", output_path)