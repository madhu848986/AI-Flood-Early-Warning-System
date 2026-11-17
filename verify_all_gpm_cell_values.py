import os
import h5py
import numpy as np
import pandas as pd

raw_folder = "datasets/raw/gpm_historical/october_2021"
csv_file = "datasets/processed/koshi_rainfall_accumulation_october_2021.csv"

csv_data = pd.read_csv(csv_file)
results = []

for date in sorted(csv_data["date"].unique()):

    date_text = pd.Timestamp(date).strftime("%Y%m%d")

    filename = next(
        (f for f in os.listdir(raw_folder)
         if date_text in f and f.endswith(".nc4")),
        None
    )

    if filename is None:
        results.append({
            "date": date_text,
            "original_cells": 0,
            "csv_cells": 0,
            "matched_cells": 0,
            "exact_matches": 0,
            "max_difference": np.nan,
            "status": "ORIGINAL FILE NOT FOUND"
        })
        continue

    filepath = os.path.join(raw_folder, filename)

    with h5py.File(filepath, "r") as hdf:

        rainfall = np.array(hdf["precipitation"][0])
        longitude = np.array(hdf["lon"])
        latitude = np.array(hdf["lat"])

        lon_mask = (longitude >= 85.0) & (longitude <= 89.5)
        lat_mask = (latitude >= 25.0) & (latitude <= 29.5)

        original = pd.DataFrame({
            "latitude": np.repeat(latitude[lat_mask], lon_mask.sum()),
            "longitude": np.tile(longitude[lon_mask], lat_mask.sum()),
            "original_rainfall": rainfall[
                np.ix_(lon_mask, lat_mask)
            ].T.flatten()
        })

    original = original[
        original["original_rainfall"] != -9999.9
    ].copy()

    current = csv_data[
        pd.to_datetime(csv_data["date"]) == pd.Timestamp(date)
    ].copy()

    for df in [original, current]:
        df["latitude"] = df["latitude"].astype(float).round(2)
        df["longitude"] = df["longitude"].astype(float).round(2)

    comparison = original.merge(
        current,
        on=["latitude", "longitude"],
        how="inner"
    )

    differences = np.abs(
        comparison["original_rainfall"].to_numpy()
        - comparison["daily_rainfall_mm"].to_numpy()
    )

    exact_matches = int(np.sum(differences == 0))

    passed = (
        len(original) == 2025
        and len(current) == 2025
        and len(comparison) == 2025
        and exact_matches == 2025
    )

    results.append({
        "date": date_text,
        "original_cells": len(original),
        "csv_cells": len(current),
        "matched_cells": len(comparison),
        "exact_matches": exact_matches,
        "max_difference": differences.max() if len(differences) else np.nan,
        "status": "PASS" if passed else "CHECK REQUIRED"
    })

report = pd.DataFrame(results)

output = "datasets/processed/gpm_all_dates_cell_validation.csv"
report.to_csv(output, index=False)

print("\nGPM ALL-DATE CELL VALIDATION")
print(report.to_string(index=False))
print("\nDates passed:", (report["status"] == "PASS").sum(), "/", len(report))
print("Saved:", output)