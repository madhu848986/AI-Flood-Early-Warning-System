
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

df = model.merge(
    modis[[
        "latitude",
        "longitude",
        "classified_pixel_count",
        "total_pixel_count"
    ]],
    on=["latitude", "longitude"],
    how="inner"
)

df["coverage_pct"] = (
    df["classified_pixel_count"] /
    df["total_pixel_count"] * 100
)

df["elevation_band"] = pd.cut(
    df["elevation_mean_m"],
    bins=[0, 500, 1000, 2000, 4000, 7000],
    labels=[
        "0-500 m",
        "500-1000 m",
        "1000-2000 m",
        "2000-4000 m",
        "4000-7000 m"
    ]
)

df["coverage_band"] = pd.cut(
    df["coverage_pct"],
    bins=[-0.01, 5, 25, 50, 75, 100],
    labels=[
        "0-5%",
        "5-25%",
        "25-50%",
        "50-75%",
        "75-100%"
    ]
)

summary = df.groupby(
    ["elevation_band", "coverage_band"],
    observed=True
).agg(
    total_cells=("observed_flood_present", "size"),
    flood_positive=("observed_flood_present", "sum")
).reset_index()

summary["flood_negative"] = (
    summary["total_cells"] - summary["flood_positive"]
)

summary["positive_rate_pct"] = (
    summary["flood_positive"] /
    summary["total_cells"] * 100
)

print("\nFLOOD RATE BY ELEVATION AND MODIS COVERAGE")
print("=" * 95)

print(summary.round(2).to_string(index=False))

print("\nANALYSIS COMPLETED")
