import pandas as pd

path = "datasets/processed/koshi_rainfall_october_13_14_2021.csv"
df = pd.read_csv(path)

print("FULL RAINFALL GRID CHECK")
print("=" * 45)

print("Total records:", len(df))
print("Unique grid cells:",
      df[["latitude", "longitude"]].drop_duplicates().shape[0])

print("\nRainfall statistics by date:")
print(
    df.groupby("date")["precipitation_mm_per_day"]
    .agg(["count", "mean", "median", "max"])
)

print("\nZero-rainfall percentage by date:")
print(
    df.assign(
        is_zero=df["precipitation_mm_per_day"].eq(0)
    )
    .groupby("date")["is_zero"]
    .mean()
    .mul(100)
)

print("\nRainfall quantiles by date:")
print(
    df.groupby("date")["precipitation_mm_per_day"]
    .quantile([0.50, 0.75, 0.90, 0.95, 0.99])
)

print("\nCoordinates with the highest rainfall:")
print(
    df.nlargest(10, "precipitation_mm_per_day")[
        ["date", "latitude", "longitude", "precipitation_mm_per_day"]
    ].to_string(index=False)
)