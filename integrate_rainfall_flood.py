import pandas as pd
import numpy as np

rainfall_path = (
    "datasets/processed/koshi_rainfall_october_13_14_2021.csv"
)

flood_path = (
    "datasets/processed/koshi_modis_flood_cell_summary.csv"
)

output_path = (
    "datasets/processed/koshi_rainfall_flood_integrated.csv"
)

rainfall = pd.read_csv(rainfall_path)
flood = pd.read_csv(flood_path)

# Normalize coordinates to avoid floating-point merge problems
rainfall["latitude"] = rainfall["latitude"].round(6)
rainfall["longitude"] = rainfall["longitude"].round(6)

flood["latitude"] = flood["latitude"].round(6)
flood["longitude"] = flood["longitude"].round(6)

# Keep the flood-observation fields needed for analysis
flood_columns = [
    "latitude",
    "longitude",
    "valid_pixels",
    "no_water_pixels",
    "reference_water_pixels",
    "recurring_flood_pixels",
    "flood_pixels",
    "flood_pixel_ratio",
    "recurring_or_flood_ratio",
]

flood_subset = flood[flood_columns].copy()

# Match each rainfall record to its grid-cell flood summary
integrated = rainfall.merge(
    flood_subset,
    on=["latitude", "longitude"],
    how="left",
    validate="many_to_one",
)

# Preserve missing observations; do not assume they are non-flooded
integrated["flood_observation_available"] = (
    integrated["valid_pixels"].notna()
)

# Create a provisional indicator only where valid observations exist.
# This means at least one MODIS pixel was classified as unusual flooding.
integrated["observed_flood_present"] = np.where(
    integrated["flood_observation_available"],
    (integrated["flood_pixels"] > 0).astype(int),
    np.nan,
)

integrated.to_csv(output_path, index=False)

print("RAINFALL-FLOOD INTEGRATION REPORT")
print("=" * 45)
print("Rainfall records:", len(rainfall))
print("Integrated records:", len(integrated))
print("Cells with flood observations:",
      integrated["flood_observation_available"].sum())
print("Records without flood observations:",
      (~integrated["flood_observation_available"]).sum())
print("Records with observed flood pixels:",
      (integrated["observed_flood_present"] == 1).sum())
print("Unique dates:", sorted(integrated["date"].unique()))
print("Output:", output_path)

print("\nSample records:")
print(integrated.head())