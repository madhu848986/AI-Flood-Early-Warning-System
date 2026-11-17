import pandas as pd
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling

INPUT_CSV = (
    "datasets/processed/koshi_event_analysis_dataset.csv"
)

ELEVATION_FILE = (
    "datasets/processed/elevation/koshi_elevation_30m.tif"
)

OUTPUT_CSV = (
    "datasets/processed/koshi_elevation_zonal_dataset.csv"
)

CELL_SIZE = 0.1

df = pd.read_csv(INPUT_CSV)

statistics = []

with rasterio.open(ELEVATION_FILE) as src:

    for _, row in df.iterrows():

        latitude = row["latitude"]
        longitude = row["longitude"]

        west = longitude - CELL_SIZE / 2
        east = longitude + CELL_SIZE / 2
        south = latitude - CELL_SIZE / 2
        north = latitude + CELL_SIZE / 2

        window = from_bounds(
            west,
            south,
            east,
            north,
            transform=src.transform
        )

        data = src.read(
            1,
            window=window,
            masked=True
        )

        values = data.compressed()

        if len(values) == 0:
            statistics.append({
                "elevation_mean_m": np.nan,
                "elevation_min_m": np.nan,
                "elevation_max_m": np.nan,
                "elevation_median_m": np.nan
            })
        else:
            statistics.append({
                "elevation_mean_m": float(np.mean(values)),
                "elevation_min_m": float(np.min(values)),
                "elevation_max_m": float(np.max(values)),
                "elevation_median_m": float(np.median(values))
            })

stats_df = pd.DataFrame(statistics)

result = pd.concat(
    [df.reset_index(drop=True), stats_df],
    axis=1
)

result.to_csv(OUTPUT_CSV, index=False)

print("Elevation zonal statistics completed.")
print("Total grid cells:", len(result))

print("\nMissing values:")
print(
    result[
        [
            "elevation_mean_m",
            "elevation_min_m",
            "elevation_max_m",
            "elevation_median_m"
        ]
    ].isna().sum()
)

print("\nElevation summary:")
print(
    result[
        [
            "elevation_mean_m",
            "elevation_min_m",
            "elevation_max_m",
            "elevation_median_m"
        ]
    ].describe().round(2)
)

print("\nSaved:", OUTPUT_CSV)