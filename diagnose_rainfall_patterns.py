import pandas as pd

path = "datasets/processed/koshi_model_analysis.csv"
df = pd.read_csv(path)

# Use one record per cell to avoid counting the same flood label twice
cells = df.drop_duplicates(
    subset=["latitude", "longitude"]
).copy()

print("RAINFALL PATTERN DIAGNOSTICS")
print("=" * 45)

print("\nUnique cells:", len(cells))

zero_pct = (
    cells["precipitation_mm_per_day"].eq(0).mean() * 100
)
print(f"Cells with zero rainfall: {zero_pct:.2f}%")

print("\nRainfall statistics by observed-flood label:")
print(
    cells.groupby("observed_flood_present")[
        "precipitation_mm_per_day"
    ].agg(["count", "mean", "median", "max"])
)

print("\nRainfall value distribution:")
print(
    cells["precipitation_mm_per_day"]
    .describe(percentiles=[0.50, 0.75, 0.90, 0.95, 0.99])
)

print("\nHighest rainfall cells:")
print(
    cells.nlargest(10, "precipitation_mm_per_day")[
        [
            "latitude",
            "longitude",
            "precipitation_mm_per_day",
            "observed_flood_present",
        ]
    ].to_string(index=False)
)