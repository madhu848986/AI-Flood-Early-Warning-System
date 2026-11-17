import pandas as pd

path = (
    "datasets/processed/"
    "koshi_rainfall_october_13_14_2021.csv"
)

df = pd.read_csv(path)

print("RAINFALL GRID CELL INSPECTION")
print("=" * 45)

print("\nFirst 10 rainfall cells:")
print(
    df[["latitude", "longitude"]]
    .drop_duplicates()
    .head(10)
    .to_string(index=False)
)

print("\nLatitude values:")
print(sorted(df["latitude"].unique())[:5])

print("\nLongitude values:")
print(sorted(df["longitude"].unique())[:5])

print("\nTotal unique grid cells:",
      df[["latitude", "longitude"]]
      .drop_duplicates()
      .shape[0])