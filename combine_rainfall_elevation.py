
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

rainfall_path = "datasets/processed/koshi_rainfall_september_2020.csv"
elevation_path = "datasets/processed/koshi_elevation_samples.csv"
output_path = "datasets/processed/koshi_rainfall_elevation.csv"

rainfall = pd.read_csv(rainfall_path)
elevation = pd.read_csv(elevation_path)

# Remove duplicate coordinates caused by overlapping tiles
elevation = elevation.drop_duplicates(
    subset=["latitude", "longitude"]
).dropna(subset=["latitude", "longitude", "elevation_m"])

# Convert latitude and longitude to radians
rain_coords = np.radians(
    rainfall[["latitude", "longitude"]].to_numpy()
)
elevation_coords = np.radians(
    elevation[["latitude", "longitude"]].to_numpy()
)

# Build the nearest-neighbor tree
tree = cKDTree(elevation_coords)

# Find nearest elevation sample for each rainfall coordinate
distances, indices = tree.query(rain_coords, k=1)

# Approximate great-circle distance in kilometres
earth_radius_km = 6371.0
distance_km = distances * earth_radius_km

rainfall["elevation_m"] = (
    elevation.iloc[indices]["elevation_m"].to_numpy()
)
rainfall["elevation_match_distance_km"] = distance_km

print("Rainfall records:", len(rainfall))
print("Records with elevation:", rainfall["elevation_m"].notna().sum())
print("\nMatching distance in kilometres:")
print(
    rainfall["elevation_match_distance_km"]
    .describe(percentiles=[0.5, 0.9, 0.95, 0.99])
)
print(
    "\nMatches farther than 2 km:",
    (rainfall["elevation_match_distance_km"] > 2).sum()
)

print("\nFirst 5 combined records:")
print(rainfall.head().to_string(index=False))

rainfall.to_csv(output_path, index=False)
print("\nSaved to:", output_path)
