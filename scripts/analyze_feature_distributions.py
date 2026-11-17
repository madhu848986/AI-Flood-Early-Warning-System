
import pandas as pd

file_path = (
    "datasets/processed/"
    "koshi_oct13_model_features_cs_v3_spatial_folds.csv"
)

df = pd.read_csv(file_path)

features = [
    "precipitation_mm_per_day",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "elevation_mean_m",
    "elevation_min_m",
    "elevation_max_m",
    "elevation_median_m",
    "elevation_range_m"
]

print("\nFEATURE DISTRIBUTION BY FLOOD CLASS")
print("=" * 70)

summary = df.groupby("observed_flood_present")[features].agg(
    ["mean", "std", "median"]
)

print(summary.round(3).to_string())

print("\nFEATURE DISTRIBUTION BY SPATIAL FOLD")
print("=" * 70)

fold_summary = df.groupby("spatial_fold")[features].mean()

print(fold_summary.round(3).to_string())

print("\nMISSING VALUES")
print(df[features].isnull().sum())

print("\nFEATURE ANALYSIS COMPLETED")
