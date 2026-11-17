
import os
import glob
import h5py
import numpy as np
import pandas as pd

folder = "datasets/raw/gpm_historical/october_2021"

files = sorted(
    glob.glob(os.path.join(folder, "*.nc4"))
)

results = []

for file_path in files:

    filename = os.path.basename(file_path)
    date = filename.split(".")[4][:8]

    with h5py.File(file_path, "r") as f:

        lon = f["lon"][:]
        lat = f["lat"][:]

        precipitation = f["precipitation"][0, :, :]

        lon_mask = (lon >= 85.0) & (lon <= 89.5)
        lat_mask = (lat >= 25.0) & (lat <= 29.5)

        regional_data = precipitation[
            np.ix_(lon_mask, lat_mask)
        ]

        fill_value = float(
            np.asarray(
                f["precipitation"].attrs["_FillValue"]
            ).reshape(-1)[0]
        )

        valid = regional_data[
            np.isfinite(regional_data)
            & (regional_data != fill_value)
        ]

        results.append({
            "date": date,
            "valid_cells": len(valid),
            "zero_cells": int(np.sum(valid == 0)),
            "mean_mm_day": float(np.mean(valid)),
            "median_mm_day": float(np.median(valid)),
            "max_mm_day": float(np.max(valid))
        })

df = pd.DataFrame(results)

print("\nORIGINAL GPM DAILY STATISTICS")
print("-----------------------------")
print(df.to_string(index=False))

print("\nTOTAL FILES:", len(df))

output_path = (
    "datasets/processed/"
    "gpm_original_daily_statistics_october_2021.csv"
)

os.makedirs("datasets/processed", exist_ok=True)

df.to_csv(output_path, index=False)

print("\nSaved:", output_path)
