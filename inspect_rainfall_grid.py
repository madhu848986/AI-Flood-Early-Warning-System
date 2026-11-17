import pandas as pd
import numpy as np

path = (
    "datasets/processed/"
    "koshi_rainfall_october_13_14_2021.csv"
)

df = pd.read_csv(path)

latitudes = np.sort(df["latitude"].unique())
longitudes = np.sort(df["longitude"].unique())

print("RAINFALL GRID INSPECTION")
print("=" * 40)

print("Unique latitudes:", len(latitudes))
print("Unique longitudes:", len(longitudes))

print(
    "Latitude spacing:",
    np.round(np.diff(latitudes)[:10], 6)
)

print(
    "Longitude spacing:",
    np.round(np.diff(longitudes)[:10], 6)
)

print("\nRecords per date:")
print(df.groupby("date").size())

print("\nDuplicate date-coordinate rows:",
      df.duplicated(["date", "latitude", "longitude"]).sum())

print("\nRainfall column statistics:")
print(df["precipitation_mm"].describe()
      if "precipitation_mm" in df.columns
      else df.select_dtypes(include="number").describe())

print("\nColumns:")
print(df.columns.tolist())