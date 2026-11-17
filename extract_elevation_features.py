import pandas as pd
import numpy as np
import rasterio

INPUT_CSV = (
    "datasets/processed/koshi_event_analysis_dataset.csv"
)

ELEVATION_FILE = (
    "datasets/processed/elevation/koshi_elevation_30m.tif"
)

OUTPUT_CSV = (
    "datasets/processed/koshi_elevation_dataset.csv"
)

df = pd.read_csv(INPUT_CSV)

with rasterio.open(ELEVATION_FILE) as src:

    coordinates = list(
        zip(df["longitude"], df["latitude"])
    )

    elevations = []

    for value in src.sample(coordinates):
        elevation = value[0]

        if elevation == src.nodata:
            elevations.append(np.nan)
        else:
            elevations.append(float(elevation))

df["elevation_m"] = elevations

df.to_csv(OUTPUT_CSV, index=False)

print("Elevation extraction completed.")
print("Total grid cells:", len(df))
print("Missing elevation values:", df["elevation_m"].isna().sum())

print("\nElevation statistics:")
print(df["elevation_m"].describe())

print("\nDataset saved at:", OUTPUT_CSV)