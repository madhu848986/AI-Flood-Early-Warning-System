import pandas as pd
import numpy as np

rainfall_path = (
    "datasets/processed/"
    "koshi_rainfall_october_13_14_2021.csv"
)

flood_path = (
    "datasets/processed/koshi_nasa_flood_pixels.csv"
)

rainfall = pd.read_csv(rainfall_path)
flood = pd.read_csv(flood_path)

rainfall_cells = (
    rainfall[["latitude", "longitude"]]
    .drop_duplicates()
    .round(6)
)

# Reproduce the current assignment method.
lat_start = rainfall_cells["latitude"].min()
lon_start = rainfall_cells["longitude"].min()

flood["assigned_latitude"] = (
    lat_start
    + np.round(
        (flood["latitude"] - lat_start) / 0.1
    ) * 0.1
).round(6)

flood["assigned_longitude"] = (
    lon_start
    + np.round(
        (flood["longitude"] - lon_start) / 0.1
    ) * 0.1
).round(6)

matched = flood.merge(
    rainfall_cells,
    left_on=["assigned_latitude", "assigned_longitude"],
    right_on=["latitude", "longitude"],
    how="inner",
)

print("COORDINATE MATCHING DIAGNOSTIC")
print("=" * 45)
print("Rainfall grid cells:", len(rainfall_cells))
print("Flood pixels:", len(flood))
print("Pixels assigned to rainfall cells:", len(matched))

print("\nRainfall latitude range:")
print(rainfall_cells["latitude"].min(),
      "to", rainfall_cells["latitude"].max())

print("\nFlood latitude range:")
print(flood["latitude"].min(),
      "to", flood["latitude"].max())

print("\nExample original flood coordinates and assignments:")
print(
    flood[
        [
            "latitude",
            "longitude",
            "assigned_latitude",
            "assigned_longitude",
        ]
    ].head(10).to_string(index=False)
)