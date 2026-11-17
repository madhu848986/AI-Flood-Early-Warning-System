import pandas as pd

path = "datasets/processed/koshi_model_analysis.csv"
df = pd.read_csv(path)

# One record per grid cell; the MODIS observation is repeated across dates
cells = df.drop_duplicates(
    subset=["latitude", "longitude"]
).copy()

cells["observed_flood_present"] = (
    cells["observed_flood_present"].astype(int)
)

print("RAINFALL–FLOOD RELATIONSHIP REPORT")
print("=" * 45)

print("\nCell counts by observed flood label:")
print(cells["observed_flood_present"].value_counts())

print("\nRainfall summary by observed flood label:")
print(
    cells.groupby("observed_flood_present")[
        "precipitation_mm_per_day"
    ].agg(["count", "mean", "median", "max"])
)

print("\nCells with non-zero rainfall by label:")
cells["rainfall_nonzero"] = (
    cells["precipitation_mm_per_day"] > 0
)

print(
    cells.groupby("observed_flood_present")[
        "rainfall_nonzero"
    ].agg(["sum", "count", "mean"])
)

print("\nFlood pixel ratio by label:")
print(
    cells.groupby("observed_flood_present")[
        "flood_pixel_ratio"
    ].agg(["mean", "median", "max"])
)