from pathlib import Path

import numpy as np
import pandas as pd
from pyhdf.SD import SD, SDC

file_path = Path(
    "datasets/raw/flood_events/nasa_flood_maps/"
    "MCDWD_L3.A2021286.h26v06.061.2025278052519.hdf"
)

output_path = Path(
    "datasets/processed/koshi_nasa_flood_pixels.csv"
)

if not file_path.exists():
    raise FileNotFoundError(f"MODIS file not found: {file_path}")

output_path.parent.mkdir(parents=True, exist_ok=True)

hdf = SD(str(file_path), SDC.READ)

try:
    flood = np.asarray(hdf.select("Flood_1Day_250m").get())
finally:
    hdf.end()

if flood.shape != (4800, 4800):
    raise ValueError(f"Unexpected grid shape: {flood.shape}")

# Geographic extent from the file metadata.
north, south = 30.0, 20.0
west, east = 80.0, 90.0

rows, cols = flood.shape

# Calculate nominal pixel-center coordinates.
latitudes = north - (
    np.arange(rows) + 0.5
) * (north - south) / rows

longitudes = west + (
    np.arange(cols) + 0.5
) * (east - west) / cols

# Approximate Koshi-region bounding box.
lat_min, lat_max = 26.0, 28.5
lon_min, lon_max = 85.0, 88.5

row_indices = np.flatnonzero(
    (latitudes >= lat_min) & (latitudes <= lat_max)
)

col_indices = np.flatnonzero(
    (longitudes >= lon_min) & (longitudes <= lon_max)
)

if len(row_indices) == 0 or len(col_indices) == 0:
    raise ValueError("No pixels found inside the selected bounding box.")

row_start, row_end = row_indices[0], row_indices[-1] + 1
col_start, col_end = col_indices[0], col_indices[-1] + 1

cropped = flood[row_start:row_end, col_start:col_end]

lat_mesh, lon_mesh = np.meshgrid(
    latitudes[row_start:row_end],
    longitudes[col_start:col_end],
    indexing="ij"
)

result = pd.DataFrame({
    "latitude": lat_mesh.ravel(),
    "longitude": lon_mesh.ravel(),
    "flood_class": cropped.ravel()
})

result.to_csv(output_path, index=False)

print("MODIS flood extraction completed.")
print("Coordinate status: nominal grid-based coordinates; validation required.")
print("Output:", output_path)
print("Grid shape:", flood.shape)
print("Extracted shape:", cropped.shape)
print("Rows:", len(result))
print("\nFlood class counts:")
print(result["flood_class"].value_counts().sort_index())
print("\nCoordinate ranges:")
print("Latitude:", result["latitude"].min(), "to", result["latitude"].max())
print("Longitude:", result["longitude"].min(), "to", result["longitude"].max())
print("\nFirst five rows:")
print(result.head())