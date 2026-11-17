import h5py
import numpy as np
import pandas as pd

gpm_path = (
    "datasets/raw/gpm_historical/october_2021/"
    "3B-DAY.MS.MRG.3IMERG.20211012-S000000-E235959.V07B.nc4"
)

csv_path = (
    "datasets/processed/"
    "koshi_pre_event_rainfall_oct12.csv"
)

with h5py.File(gpm_path, "r") as f:

    lon = f["lon"][:]
    lat = f["lat"][:]

    precipitation = f["precipitation"][0, :, :]

    lon_mask = (lon >= 85) & (lon <= 89.5)
    lat_mask = (lat >= 25) & (lat <= 29.5)

    original = precipitation[
        np.ix_(lon_mask, lat_mask)
    ]

    regional_lon = lon[lon_mask]
    regional_lat = lat[lat_mask]

    original_df = pd.DataFrame({
        "longitude": np.repeat(regional_lon, len(regional_lat)),
        "latitude": np.tile(regional_lat, len(regional_lon)),
        "original_rainfall_mm": original.flatten()
    })

csv_df = pd.read_csv(csv_path)

# Convert both coordinate columns to float64
for df in [original_df, csv_df]:

    df["latitude"] = (
        df["latitude"].astype("float64").round(2)
    )

    df["longitude"] = (
        df["longitude"].astype("float64").round(2)
    )

comparison = original_df.merge(
    csv_df[
        ["latitude", "longitude", "daily_rainfall_mm"]
    ],
    on=["latitude", "longitude"],
    how="outer",
    indicator=True
)

matched = comparison[
    comparison["_merge"] == "both"
].copy()

matched["difference"] = (
    matched["original_rainfall_mm"]
    - matched["daily_rainfall_mm"]
)

exact = np.isclose(
    matched["original_rainfall_mm"],
    matched["daily_rainfall_mm"],
    atol=0.00001
)

print("\nGPM CELL-BY-CELL VALIDATION")
print("---------------------------")

print("Original cells:", len(original_df))
print("CSV cells:", len(csv_df))
print("Matched cells:", len(matched))

print(
    "Unmatched original:",
    (comparison["_merge"] == "left_only").sum()
)

print(
    "Unmatched CSV:",
    (comparison["_merge"] == "right_only").sum()
)

print("Exact rainfall matches:", exact.sum())

print(
    "Maximum absolute difference:",
    matched["difference"].abs().max()
)

output_path = (
    "datasets/processed/"
    "gpm_oct12_cell_by_cell_comparison.csv"
)

comparison.to_csv(output_path, index=False)

print("\nSaved:", output_path)