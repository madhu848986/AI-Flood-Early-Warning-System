
import pandas as pd
import numpy as np
import rasterio
from rasterio.warp import transform

rainfall_file = "datasets/processed/koshi_pre_event_rainfall_oct12.csv"
elevation_file = "datasets/processed/elevation/koshi_elevation_30m.tif"
output_file = "datasets/processed/koshi_all_grid_elevation.csv"

df = pd.read_csv(rainfall_file)

with rasterio.open(elevation_file) as src:

    if src.crs is None:
        raise ValueError("Elevation raster CRS is missing")

    if src.crs.to_string() != "EPSG:4326":
        x, y = transform(
            "EPSG:4326",
            src.crs,
            df["longitude"].tolist(),
            df["latitude"].tolist()
        )
    else:
        x = df["longitude"].tolist()
        y = df["latitude"].tolist()

    coordinates = list(zip(x, y))
    elevations = np.array(
        [value[0] for value in src.sample(coordinates)],
        dtype=float
    )

    nodata = src.nodata

    if nodata is not None:
        elevations[elevations == nodata] = np.nan

df["elevation_mean_m"] = elevations

print("TOTAL GRID CELLS:", len(df))
print("Valid elevations:", df["elevation_mean_m"].notna().sum())
print("Missing elevations:", df["elevation_mean_m"].isna().sum())

print("\nELEVATION STATISTICS:")
print(df["elevation_mean_m"].describe().round(2))

df.to_csv(output_file, index=False)

print("\nSaved:", output_file)
