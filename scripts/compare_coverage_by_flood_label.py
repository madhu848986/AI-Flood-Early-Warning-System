
import pandas as pd

model_file = (
    "datasets/processed/"
    "koshi_oct13_model_features_cs_v3_spatial_folds.csv"
)

modis_file = (
    "datasets/processed/"
    "modis_flood_by_rainfall_cell_cs_quality.csv"
)

model = pd.read_csv(model_file)
modis = pd.read_csv(modis_file)

modis["coverage_pct"] = (
    modis["classified_pixel_count"] /
    modis["total_pixel_count"] * 100
)

df = model.merge(
    modis[[
        "latitude",
        "longitude",
        "coverage_pct",
        "classified_pixel_count",
        "class_3_count"
    ]],
    on=["latitude", "longitude"],
    how="inner"
)

print("\nCOVERAGE BY FLOOD LABEL")
print("=" * 85)

print(
    df.groupby("observed_flood_present").agg(
        cells=("coverage_pct", "count"),
        mean_coverage=("coverage_pct", "mean"),
        median_coverage=("coverage_pct", "median"),
        min_coverage=("coverage_pct", "min"),
        max_coverage=("coverage_pct", "max")
    ).round(2)
)

print("\nCOVERAGE BY ELEVATION BAND")
print("=" * 85)

df["elevation_band"] = pd.cut(
    df["elevation_mean_m"],
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

print(
    df.groupby(
        ["elevation_band", "observed_flood_present"],
        observed=False
    ).agg(
        cells=("coverage_pct", "count"),
        mean_coverage=("coverage_pct", "mean"),
        median_coverage=("coverage_pct", "median")
    ).round(2)
)

print("\nCOMPARISON COMPLETED")
