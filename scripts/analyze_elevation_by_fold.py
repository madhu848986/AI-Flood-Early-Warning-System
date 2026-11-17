
import pandas as pd

file_path = (
    "datasets/processed/"
    "koshi_oct13_model_features_cs_v3_spatial_folds.csv"
)

df = pd.read_csv(file_path)

print("\nELEVATION ANALYSIS BY FOLD AND FLOOD CLASS")
print("=" * 75)

summary = df.groupby(
    ["spatial_fold", "observed_flood_present"]
)["elevation_mean_m"].agg(
    ["count", "mean", "median", "min", "max"]
)

print(summary.round(2).to_string())

print("\nGEOGRAPHICAL COVERAGE BY FOLD")
print("=" * 75)

geo = df.groupby("spatial_fold").agg(
    min_latitude=("latitude", "min"),
    max_latitude=("latitude", "max"),
    min_longitude=("longitude", "min"),
    max_longitude=("longitude", "max"),
    total_cells=("latitude", "count")
)

print(geo.round(3).to_string())

print("\nELEVATION ANALYSIS COMPLETED")
