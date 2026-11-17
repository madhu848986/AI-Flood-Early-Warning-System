
import pandas as pd

input_path = "datasets/processed/koshi_rainfall_elevation.csv"
output_path = "datasets/processed/koshi_rainfall_features.csv"

df = pd.read_csv(input_path)
df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(
    ["latitude", "longitude", "date"]
).reset_index(drop=True)

# Calculate rainfall features separately for each grid cell
grouped = df.groupby(["latitude", "longitude"])[
    "precipitation_mm_per_day"
]

df["previous_day_rainfall_mm"] = grouped.shift(1)

df["rainfall_3day_mm"] = grouped.transform(
    lambda s: s.rolling(3, min_periods=3).sum()
)

df["rainfall_7day_mm"] = grouped.transform(
    lambda s: s.rolling(7, min_periods=7).sum()
)

df.to_csv(output_path, index=False)

print("Feature dataset saved to:", output_path)
print("Total records:", len(df))
print("\nMissing values in rainfall features:")
print(
    df[
        [
            "previous_day_rainfall_mm",
            "rainfall_3day_mm",
            "rainfall_7day_mm"
        ]
    ].isna().sum()
)

print("\nLast 5 records:")
print(df.tail().to_string(index=False))
