import os
import glob
import h5py
import numpy as np
import pandas as pd

folder = "datasets/raw/gpm_historical/october_2021"

files = sorted(glob.glob(os.path.join(folder, "*.nc4")))

results = []

for file_path in files:

    filename = os.path.basename(file_path)
    date = filename.split(".")[4][:8]

    with h5py.File(file_path, "r") as f:

        lon = f["lon"][:]
        lat = f["lat"][:]

        precipitation = f["precipitation"][0, :, :]
        retrieval_count = f["precipitation_cnt"][0, :, :]

        lon_mask = (lon >= 85.0) & (lon <= 89.5)
        lat_mask = (lat >= 25.0) & (lat <= 29.5)

        rainfall = precipitation[
            np.ix_(lon_mask, lat_mask)
        ]

        counts = retrieval_count[
            np.ix_(lon_mask, lat_mask)
        ]

        fill_value = float(
            np.asarray(
                f["precipitation"].attrs["_FillValue"]
            ).reshape(-1)[0]
        )

        valid = (
            np.isfinite(rainfall)
            & (rainfall != fill_value)
        )

        zero = valid & (rainfall == 0)
        positive = valid & (rainfall > 0)

        results.append({
            "date": date,
            "total_cells": rainfall.size,
            "valid_cells": int(valid.sum()),
            "zero_rain_cells": int(zero.sum()),
            "zero_with_valid_count": int(
                np.sum(zero & (counts > 0))
            ),
            "zero_with_zero_count": int(
                np.sum(zero & (counts == 0))
            ),
            "positive_rain_cells": int(positive.sum()),
            "positive_with_zero_count": int(
                np.sum(positive & (counts == 0))
            ),
            "retrieval_count_min": float(counts[valid].min()),
            "retrieval_count_max": float(counts[valid].max())
        })

df = pd.DataFrame(results)

print("\nGPM RETRIEVAL COUNT QUALITY REPORT")
print("----------------------------------")
print(df.to_string(index=False))

print("\nTOTAL FILES:", len(df))

output_path = (
    "datasets/processed/"
    "gpm_retrieval_count_quality_report.csv"
)

os.makedirs("datasets/processed", exist_ok=True)

df.to_csv(output_path, index=False)

print("\nSaved:", output_path)