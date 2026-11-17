
import h5netcdf
import numpy as np
import pandas as pd
import os
import glob
import re

# Input and output folders
input_folder = os.path.join(
    "datasets", "raw", "gpm_historical"
)

output_folder = os.path.join(
    "datasets", "processed"
)

os.makedirs(output_folder, exist_ok=True)

# Preliminary Koshi Basin study-area bounding box
min_lon, max_lon = 85.0, 89.5
min_lat, max_lat = 25.0, 29.5

all_data = []

files = sorted(
    glob.glob(os.path.join(input_folder, "*.nc4"))
)

if not files:
    print("ERROR: No .nc4 files found in", input_folder)
    raise SystemExit(1)

for file_path in files:
    filename = os.path.basename(file_path)
    print("\nProcessing:", filename)

    # Extract the 8-digit date from the filename
    match = re.search(r"\.(\d{8})-S", filename)

    if not match:
        print("Could not identify date; skipping file.")
        continue

    date = pd.to_datetime(
        match.group(1),
        format="%Y%m%d",
        errors="coerce"
    )

    if pd.isna(date):
        print("Invalid date; skipping file.")
        continue

    try:
        with h5netcdf.File(
            file_path,
            mode="r",
            backend="pyfive"
        ) as f:

            # Read coordinate arrays
            lon = np.asarray(f.variables["lon"][:])
            lat = np.asarray(f.variables["lat"][:])

            # Read precipitation.
            # Original variable shape: (time, lon, lat)
            rain = np.asarray(
                f.variables["precipitation"][0, :, :]
            ).T

            # Select coordinates within the bounding box
            lon_indices = np.where(
                (lon >= min_lon) & (lon <= max_lon)
            )[0]

            lat_indices = np.where(
                (lat >= min_lat) & (lat <= max_lat)
            )[0]

            if len(lon_indices) == 0 or len(lat_indices) == 0:
                print("No grid points found in the selected area.")
                continue

            # Extract the selected rainfall grid
            rain_subset = rain[
                np.ix_(lat_indices, lon_indices)
            ]

            # Exclude missing and invalid values
            valid = (
                np.isfinite(rain_subset)
                & (rain_subset != -9999.9)
                & (rain_subset >= 0)
            )

            # Create matching latitude and longitude grids
            lat_grid, lon_grid = np.meshgrid(
                lat[lat_indices],
                lon[lon_indices],
                indexing="ij"
            )

            # Store valid grid cells for this date
            day_data = pd.DataFrame({
                "date": date,
                "latitude": lat_grid[valid],
                "longitude": lon_grid[valid],
                "precipitation_mm_per_day": rain_subset[valid]
            })

            if day_data.empty:
                print("No valid rainfall values for this date.")
                continue

            all_data.append(day_data)

            print("Date:", date.strftime("%Y-%m-%d"))
            print("Valid grid cells:", len(day_data))

    except Exception as error:
        print("Error processing file:", repr(error))

# Combine all daily data and save to CSV
if all_data:
    result = pd.concat(all_data, ignore_index=True)

    output_path = os.path.join(
        output_folder,
        "koshi_rainfall_september_2020.csv"
    )

    result.to_csv(output_path, index=False)

    print("\n--- EXTRACTION SUMMARY ---")
    print("Files discovered:", len(files))
    print("Dates extracted:", result["date"].nunique())
    print("Total records:", len(result))
    print("Missing values:\n", result.isnull().sum())
    print("Rainfall summary:")
    print(result["precipitation_mm_per_day"].describe())
    print("\nFirst five records:")
    print(result.head())
    print("\nCSV saved to:", output_path)

else:
    print("\nNo valid rainfall records extracted.")
