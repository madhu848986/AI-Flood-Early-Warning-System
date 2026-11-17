
import pandas as pd

file_path = (
    "datasets/processed/"
    "modis_flood_by_rainfall_cell_cs_quality.csv"
)

df = pd.read_csv(file_path)

# Select cells containing class-3 flood pixels
positive = df[df["class_3_count"] > 0].copy()

positive["classified_coverage_pct"] = (
    positive["classified_pixel_count"] /
    positive["total_pixel_count"] * 100
)

positive["flood_pct_of_classified"] = (
    positive["class_3_count"] /
    positive["classified_pixel_count"] * 100
)

positive["elevation_band"] = "Not joined"

model_path = (
    "datasets/processed/"
    "koshi_oct13_model_features_cs_v3_spatial_folds.csv"
)

model = pd.read_csv(model_path)

positive = positive.merge(
    model[[
        "latitude",
        "longitude",
        "elevation_mean_m"
    ]],
    on=["latitude", "longitude"],
    how="left"
)

positive["elevation_band"] = pd.cut(
    positive["elevation_mean_m"],
    bins=[0, 500, 1000, 2000, 4000, 7000],
    labels=[
        "0-500 m",
        "500-1000 m",
        "1000-2000 m",
        "2000-4000 m",
        "4000-7000 m"
    ]
)

print("\nFLOOD-POSITIVE CELL COVERAGE ANALYSIS")
print("=" * 90)

print("Total positive cells:", len(positive))

print("\nCLASSIFIED COVERAGE SUMMARY (%)")
print(positive["classified_coverage_pct"].describe().round(2))

print("\nFLOOD PIXEL PERCENTAGE SUMMARY")
print(positive["flood_pct_of_classified"].describe().round(2))

print("\nHIGH-ALTITUDE POSITIVE CELLS")
high = positive[positive["elevation_mean_m"] >= 4000]

columns = [
    "latitude",
    "longitude",
    "elevation_mean_m",
    "classified_pixel_count",
    "unknown_pixel_count",
    "classified_coverage_pct",
    "class_3_count",
    "flood_pct_of_classified"
]

print(high[columns].round(3).to_string(index=False))

print("\nPOSITIVE CELLS BY ELEVATION BAND")
print(
    positive.groupby(
        "elevation_band",
        observed=False
    ).agg(
        cells=("class_3_count", "size"),
        mean_coverage=("classified_coverage_pct", "mean"),
        mean_flood_percentage=("flood_pct_of_classified", "mean")
    ).round(3)
)

print("\nANALYSIS COMPLETED")
