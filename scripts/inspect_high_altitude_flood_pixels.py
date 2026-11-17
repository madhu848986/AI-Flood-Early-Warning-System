
import pandas as pd
import numpy as np

model_file = (
    "datasets/processed/"
    "koshi_oct13_model_features_cs_v3_spatial_folds.csv"
)

pixel_file = (
    "datasets/processed/"
    "koshi_nasa_flood_pixels_quality_cs.csv"
)

model = pd.read_csv(model_file)
pixels = pd.read_csv(pixel_file)

high = model[
    (model["observed_flood_present"] == 1) &
    (model["elevation_mean_m"] >= 4000)
].copy()

pixels["cell_latitude"] = (
    np.floor(pixels["latitude"] * 10) / 10 + 0.05
).round(2)

pixels["cell_longitude"] = (
    np.floor(pixels["longitude"] * 10) / 10 + 0.05
).round(2)

selected = pixels.merge(
    high[[
        "latitude",
        "longitude",
        "elevation_mean_m"
    ]].rename(columns={
        "latitude": "cell_latitude",
        "longitude": "cell_longitude"
    }),
    on=["cell_latitude", "cell_longitude"],
    how="inner"
)

print("\nHIGH-ALTITUDE MODIS PIXEL INSPECTION")
print("=" * 90)

print("Matched MODIS pixels:", len(selected))

print("\nPIXEL CLASS COUNTS")
print(selected["flood_class"].value_counts().sort_index())

flood_pixels = selected[
    selected["flood_class"] == 3
].copy()

print("\nCLASS-3 PIXEL LOCATIONS")
print("-" * 90)

print("Class-3 pixels:", len(flood_pixels))

print(
    flood_pixels[[
        "latitude",
        "longitude",
        "cell_latitude",
        "cell_longitude",
        "elevation_mean_m"
    ]].round(5).to_string(index=False)
)

print("\nCLASS-3 PIXEL SPREAD BY GRID CELL")
print("-" * 90)

summary = flood_pixels.groupby(
    ["cell_latitude", "cell_longitude"]
).agg(
    flood_pixels=("flood_class", "size"),
    min_pixel_lat=("latitude", "min"),
    max_pixel_lat=("latitude", "max"),
    min_pixel_lon=("longitude", "min"),
    max_pixel_lon=("longitude", "max")
).reset_index()

print(summary.round(5).to_string(index=False))

print("\nINSPECTION COMPLETED")
