
import pandas as pd

file_path = (
    "datasets/processed/"
    "koshi_oct13_model_features_cs_v3_spatial_folds.csv"
)

df = pd.read_csv(file_path)

positive = df[df["observed_flood_present"] == 1].copy()

print("\nFLOOD-POSITIVE CELLS ABOVE 4000 METRES")
print("=" * 90)

high = positive[
    positive["elevation_mean_m"] >= 4000
].sort_values("elevation_mean_m", ascending=False)

columns = [
    "spatial_fold",
    "latitude",
    "longitude",
    "precipitation_mm_per_day",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "elevation_mean_m",
    "elevation_min_m",
    "elevation_max_m",
    "elevation_median_m",
    "elevation_range_m"
]

print("High-altitude positive cells:", len(high))
print(high[columns].round(3).to_string(index=False))

print("\nPOSITIVE CELLS BY ELEVATION BAND")
print("=" * 90)

positive["elevation_band"] = pd.cut(
    positive["elevation_mean_m"],
    bins=[0, 500, 1000, 2000, 3000, 4000, 7000],
    labels=[
        "0-500 m",
        "500-1000 m",
        "1000-2000 m",
        "2000-3000 m",
        "3000-4000 m",
        "4000-7000 m"
    ]
)

print(positive["elevation_band"].value_counts().sort_index())

print("\nINSPECTION COMPLETED")
