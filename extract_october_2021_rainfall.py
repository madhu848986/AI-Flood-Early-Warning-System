
import h5netcdf
import numpy as np
import pandas as pd
import os
import glob

input_folder = os.path.join(
    "datasets", "raw", "gpm_historical", "october_2021"
)

output_folder = os.path.join(
    "datasets", "processed"
)

os.makedirs(output_folder, exist_ok=True)

# Koshi Basin bounding box
min_lon, max_lon = 85.0, 89.5
min_lat, max_lat = 25.0, 29.5

all_data = []

files = sorted(
    glob.glob(os.path.join(input_folder, "*.nc4"))
)

if not files:
    print("No .nc4 files found.")
    raise SystemExit

for file_path in files:
    filename = os.path.basename(file_path)
    print("\nProcessing:", filename)

    with h5netcdf.File(file_path, mode="r") as f:
        print("Available variables:", list(f.variables))

        lon = np.array(f.variables["lon"][:])
        lat = np.array(f.variables["lat"][:])

        # Inspect the actual variable dimensions
        if "precipitation" not in f.variables:
            print("Precipitation variable not found; skipping.")
            continue

        variable = f.variables["precipitation"]
        print("Precipitation shape:", variable.shape)

        rain = np.array(variable[:]).squeeze()

        if rain.shape == (len(lat), len(lon)):
            pass
        elif rain.shape == (len(lon), len(lat)):
            rain = rain.T
        else:
            print("Unexpected rainfall dimensions; skipping.")
            continue

        lon_indices = np.where(
            (lon >= min_lon) & (lon <= max_lon)
        )[0]

        lat_indices = np.where(
            (lat >= min_lat) & (lat <= max_lat)
        )[0]

        if len(lon_indices) == 0 or len(lat_indices) == 0:
            print("No coordinates inside the bounding box.")
            continue

        rain_subset = rain[
            np.ix_(lat_indices, lon_indices)
        ]

        lat_grid, lon_grid = np.meshgrid(
            lat[lat_indices],
            lon[lon_indices],
            indexing="ij"
        )

        # Extract YYYYMMDD from the IMERG filename
        date_text = filename.split(".")[4]
        date_text = date_text.split("-")[0]

        date = pd.to_datetime(
            date_text,
            format="%Y%m%d",
            errors="coerce"
        )

        if pd.isna(date):
            print("Invalid date; skipping.")
            continue

        valid = (
            np.isfinite(rain_subset)
            & (rain_subset >= 0)
        )

        day_data = pd.DataFrame({
            "date": np.repeat(date, int(valid.sum())),
            "latitude": lat_grid[valid],
            "longitude": lon_grid[valid],
            "precipitation_mm_per_day": rain_subset[valid]
        })

        print("Date:", date.date())
        print("Valid grid cells:", len(day_data))

        all_data.append(day_data)

if all_data:
    result = pd.concat(all_data, ignore_index=True)

    output_path = os.path.join(
        output_folder,
        "koshi_rainfall_october_13_14_2021.csv"
    )

    result.to_csv(output_path, index=False)

    print("\nExtraction completed.")
    print("Total records:", len(result))
    print("Dates:", sorted(
        result["date"].dt.strftime("%Y-%m-%d").unique()
    ))
    print("Output:", output_path)
    print(result.head())

else:
    print("No valid rainfall records extracted.")
