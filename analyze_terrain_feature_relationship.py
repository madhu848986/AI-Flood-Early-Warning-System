import pandas as pd

INPUT_CSV = (
    "datasets/processed/koshi_ml_dataset_with_terrain_range.csv"
)

df = pd.read_csv(INPUT_CSV)

features = [
    "elevation_mean_m",
    "elevation_range_m",
    "latitude",
    "longitude",
    "rainfall_3day_mm",
    "rainfall_7day_mm"
]

print("FEATURE CORRELATION MATRIX")
print("--------------------------")

correlation = df[features].corr()

print(correlation.round(3))

print("\nElevation range by flood label:")
print(
    df.groupby("flood_label")["elevation_range_m"]
    .describe()
    .round(2)
)

correlation.to_csv(
    "datasets/processed/terrain_feature_correlation.csv"
)

print("\nSaved: datasets/processed/terrain_feature_correlation.csv")