
from pathlib import Path
import re

import numpy as np
import pandas as pd
import h5netcdf


# --------------------------------------------------
# 1. PATHS AND SETTINGS
# --------------------------------------------------

INPUT_DIR = Path(
    "datasets/raw/gpm_historical/october_2021"
)

OUTPUT_DIR = Path(
    "datasets/processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "koshi_rainfall_accumulation_october_2021.csv"
)

MIN_LON = 85.0
MAX_LON = 89.5

MIN_LAT = 25.0
MAX_LAT = 29.5

EXPECTED_DAYS = 9


# --------------------------------------------------
# 2. FIND DAILY GPM FILES
# --------------------------------------------------

files = sorted(
    INPUT_DIR.glob("3B-DAY.MS.MRG.3IMERG.*.nc4")
)

if not files:
    raise FileNotFoundError(
        f"No GPM daily files found in {INPUT_DIR}"
    )

print("GPM DAILY RAINFALL FILES")
print("------------------------")
print("Files found:", len(files))

if len(files) != EXPECTED_DAYS:
    raise ValueError(
        f"Expected {EXPECTED_DAYS} files, "
        f"but found {len(files)}"
    )


# --------------------------------------------------
# 3. EXTRACT DAILY RAINFALL
# --------------------------------------------------

all_days = []

for file in files:

    match = re.search(
        r"IMERG\.(\d{8})-",
        file.name
    )

    if not match:
        print("Skipping invalid filename:", file.name)
        continue

    date = pd.to_datetime(
        match.group(1),
        format="%Y%m%d"
    )

    print("\nProcessing:", date.date())

    with h5netcdf.File(
        file,
        mode="r",
        backend="pyfive"
    ) as data:

        lat = np.asarray(
            data.variables["lat"][:]
        )

        lon = np.asarray(
            data.variables["lon"][:]
        )

        rainfall = np.asarray(
            data.variables["precipitation"][0, :, :]
        ).T.astype(float)

        # Negative values are treated as invalid.
        rainfall[rainfall < 0] = np.nan

        # Select Koshi Basin bounding box.
        lat_mask = (
            (lat >= MIN_LAT)
            & (lat <= MAX_LAT)
        )

        lon_mask = (
            (lon >= MIN_LON)
            & (lon <= MAX_LON)
        )

        rainfall = rainfall[
            np.ix_(lat_mask, lon_mask)
        ]

        selected_lat = lat[lat_mask]
        selected_lon = lon[lon_mask]

        lon_grid, lat_grid = np.meshgrid(
            selected_lon,
            selected_lat
        )

        day_df = pd.DataFrame({
            "date": date,
            "latitude": lat_grid.ravel(),
            "longitude": lon_grid.ravel(),
            "daily_rainfall_mm": rainfall.ravel()
        })

        all_days.append(day_df)

        print(
            "Grid cells:",
            len(day_df)
        )

        print(
            "Valid rainfall values:",
            day_df["daily_rainfall_mm"].notna().sum()
        )

        print(
            "Missing rainfall values:",
            day_df["daily_rainfall_mm"].isna().sum()
        )


# --------------------------------------------------
# 4. COMBINE ALL DAILY DATA
# --------------------------------------------------

if not all_days:
    raise ValueError(
        "No valid rainfall data was extracted."
    )

df = pd.concat(
    all_days,
    ignore_index=True
)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(
    [
        "latitude",
        "longitude",
        "date"
    ]
).reset_index(drop=True)


# --------------------------------------------------
# 5. CHECK DUPLICATE RECORDS
# --------------------------------------------------

duplicates = df.duplicated(
    subset=[
        "latitude",
        "longitude",
        "date"
    ]
).sum()

if duplicates > 0:
    raise ValueError(
        f"Found {duplicates} duplicate grid-date records."
    )

print("\nDuplicate records:", duplicates)


# --------------------------------------------------
# 6. CALCULATE RAINFALL ACCUMULATIONS
# --------------------------------------------------

grouped = df.groupby(
    [
        "latitude",
        "longitude"
    ]
)["daily_rainfall_mm"]


# Current day + previous 2 days.
df["rainfall_3day_mm"] = grouped.transform(
    lambda s: s.rolling(
        window=3,
        min_periods=3
    ).sum()
)


# Current day + previous 6 days.
df["rainfall_7day_mm"] = grouped.transform(
    lambda s: s.rolling(
        window=7,
        min_periods=7
    ).sum()
)


# --------------------------------------------------
# 7. VERIFY DATE COVERAGE
# --------------------------------------------------

unique_dates = sorted(
    df["date"].dt.strftime("%Y-%m-%d").unique()
)

print("\nDATE COVERAGE")
print("-------------")

print("Start date:", df["date"].min().date())
print("End date:", df["date"].max().date())

print("Unique dates:", len(unique_dates))

for date in unique_dates:
    print(date)


# --------------------------------------------------
# 8. RAINFALL DATA QUALITY
# --------------------------------------------------

print("\nRAINFALL DATA QUALITY")
print("---------------------")

rainfall_columns = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm"
]

print("\nMissing values:")

print(
    df[rainfall_columns].isna().sum()
)

print("\nPositive rainfall records:")

for column in rainfall_columns:

    print(
        column,
        ":",
        (df[column] > 0).sum()
    )


# --------------------------------------------------
# 9. DAILY RAINFALL SUMMARY
# --------------------------------------------------

print("\nDAILY RAINFALL SUMMARY")
print("----------------------")

daily_summary = (
    df.groupby("date")["daily_rainfall_mm"]
    .agg(
        count="count",
        mean="mean",
        median="median",
        maximum="max"
    )
)

print(
    daily_summary.round(3)
)


# --------------------------------------------------
# 10. ACCUMULATION SUMMARY
# --------------------------------------------------

print("\nACCUMULATION SUMMARY")
print("--------------------")

print(
    df[rainfall_columns].describe().round(3)
)


# --------------------------------------------------
# 11. SAVE OUTPUT
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nPROCESS COMPLETED")
print("-----------------")

print("Total records:", len(df))

print(
    "Grid cells:",
    df[
        ["latitude", "longitude"]
    ].drop_duplicates().shape[0]
)

print("Saved:", OUTPUT_FILE)
