
from pathlib import Path

import numpy as np
import pandas as pd
from pyhdf.SD import SD, SDC

file_path = Path(
    "datasets/raw/flood_events/nasa_flood_maps/"
    "MCDWD_L3.A2021286.h26v06.061.2025278052519.hdf"
)

output_path = Path(
    "datasets/processed/koshi_nasa_flood_pixels_quality_cs.csv"
)

hdf = SD(str(file_path), SDC.READ)

try:
    flood = np.asarray(
        hdf.select("FloodCS_1Day_250m").get()
    )

    valid = np.asarray(
        hdf.select("ValidCountsCS_1Day_250m").get()
    )

    total = np.asarray(
        hdf.select("TotalCounts_1Day_250m").get()
    )

    water = np.asarray(
        hdf.select("WaterCountsCS_1Day_250m").get()
    )

finally:
    hdf.end()

if not (
    flood.shape == valid.shape == total.shape == water.shape
    == (4800, 4800)
):
    raise ValueError("Unexpected dataset dimensions.")

rows, cols = flood.shape

latitudes = 30.0 - (
    np.arange(rows) + 0.5
) * 10.0 / rows

longitudes = 80.0 + (
    np.arange(cols) + 0.5
) * 10.0 / cols

row_indices = np.flatnonzero(
    (latitudes >= 26.0) & (latitudes <= 28.5)
)

col_indices = np.flatnonzero(
    (longitudes >= 85.0) & (longitudes <= 88.5)
)

r0, r1 = row_indices[0], row_indices[-1] + 1
c0, c1 = col_indices[0], col_indices[-1] + 1

lat_mesh, lon_mesh = np.meshgrid(
    latitudes[r0:r1],
    longitudes[c0:c1],
    indexing="ij"
)

result = pd.DataFrame({
    "latitude": lat_mesh.ravel(),
    "longitude": lon_mesh.ravel(),
    "flood_class": flood[r0:r1, c0:c1].ravel(),
    "valid_observations": valid[r0:r1, c0:c1].ravel(),
    "total_observations": total[r0:r1, c0:c1].ravel(),
    "water_observations": water[r0:r1, c0:c1].ravel()
})

output_path.parent.mkdir(parents=True, exist_ok=True)
result.to_csv(output_path, index=False)

print("CLOUD-SHADOW-CORRECTED QUALITY EXTRACTION COMPLETED")
print("Output:", output_path)
print("Rows:", len(result))

print("\nFlood classes:")
print(result["flood_class"].value_counts().sort_index())

print("\nValid observation statistics:")
print(result["valid_observations"].describe())

print("\nTotal observation statistics:")
print(result["total_observations"].describe())

print("\nWater observation statistics:")
print(result["water_observations"].describe())

print("\nFlood class and observation summary:")
print(
    result.groupby("flood_class")[
        ["valid_observations", "total_observations", "water_observations"]
    ].agg(["count", "min", "median", "max"])
)

print("\nFirst five rows:")
print(result.head())
