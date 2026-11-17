
import pandas as pd

model_file = (
    "datasets/processed/"
    "koshi_oct13_model_features_cs_v3_spatial_folds.csv"
)

modis_file = (
    "datasets/processed/"
    "modis_flood_by_rainfall_grid_cs_quality.csv"
)

# Use the actual aggregation filename
modis_file = (
    "datasets/processed/"
    "modis_flood_by_rainfall_cell_cs_quality.csv"
)

model = pd.read_csv(model_file)
modis = pd.read_csv(modis_file)

# Select flood-positive cells above 4000 metres
high = model[
    (model["observed_flood_present"] == 1) &
    (model["elevation_mean_m"] >= 4000)
].copy()

# Match coordinates after rounding
high["latitude_key"] = high["latitude"].round(2)
high["longitude_key"] = high["longitude"].round(2)

modis["latitude_key"] = modis["latitude"].round(2)
modis["longitude_key"] = modis["longitude"].round(2)

columns = [
    "latitude_key",
    "longitude_key",
    "class_0_count",
    "class_1_count",
    "class_2_count",
    "class_3_count",
    "class_255_count",
    "classified_pixel_count",
    "unknown_pixel_count",
    "valid_observations_mean",
    "total_observations_mean",
    "water_observations_mean"
]

result = high.merge(
    modis[columns],
    on=["latitude_key", "longitude_key"],
    how="left"
)

print("\nHIGH-ALTITUDE MODIS LABEL VALIDATION")
print("=" * 100)

print("High-altitude positive cells:", len(high))
print("Matched MODIS cells:", result["class_3_count"].notna().sum())

display_columns = [
    "spatial_fold",
    "latitude",
    "longitude",
    "elevation_mean_m",
    "class_1_count",
    "class_2_count",
    "class_3_count",
    "class_255_count",
    "classified_pixel_count",
    "unknown_pixel_count",
    "valid_observations_mean",
    "water_observations_mean"
]

print(
    result[display_columns]
    .round(3)
    .to_string(index=False)
)

print("\nCLASS 3 COUNT SUMMARY")
print(result["class_3_count"].describe())

print("\nCLASS 2 COUNT SUMMARY")
print(result["class_2_count"].describe())

print("\nVALIDATION COMPLETED")
