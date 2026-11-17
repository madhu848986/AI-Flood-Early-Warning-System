
import os
import pandas as pd

files = {
    "Rainfall": "datasets/processed/koshi_rainfall_september_2020.csv",
    "Elevation": "datasets/processed/koshi_elevation_samples.csv"
}

for name, path in files.items():
    print("\n", name.upper())
    print("-" * 40)

    df = pd.read_csv(path)

    print("Rows:", len(df))
    print("Columns:", list(df.columns))
    print("Latitude range:",
          df["latitude"].min(), "to", df["latitude"].max())
    print("Longitude range:",
          df["longitude"].min(), "to", df["longitude"].max())
    print("\nFirst 3 records:")
    print(df.head(3).to_string(index=False))
