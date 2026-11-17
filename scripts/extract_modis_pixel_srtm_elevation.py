
import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache

model_file = Path(
    "datasets/processed/"
    "koshi_oct13_model_features_cs_v3_spatial_folds.csv"
)

pixel_file = Path(
    "datasets/processed/"
    "koshi_nasa_flood_pixels_quality_cs.csv"
)

elevation_folder = Path("datasets/raw/elevation")

output_file = Path(
    "datasets/processed/"
    "koshi_high_altitude_modis_pixels_with_srtm.csv"
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

@lru_cache(maxsize=None)
def load_tile(lat_degree, lon_degree):
    lat_prefix = "N" if lat_degree >= 0 else "S"
    lon_prefix = "E" if lon_degree >= 0 else "W"

    filename = (
        f"{lat_prefix}{abs(lat_degree):02d}"
        f"{lon_prefix}{abs(lon_degree):03d}.hgt"
    )

    path = elevation_folder / filename

    if not path.exists():
        return None

    data = np.fromfile(path, dtype=">i2")

    if data.size != 3601 * 3601:
        raise ValueError(f"Unexpected HGT size: {path}")

    return data.reshape(3601, 3601)

def get_elevation(lat, lon):
    lat_degree = int(np.floor(lat))
    lon_degree = int(np.floor(lon))

    tile = load_tile(lat_degree, lon_degree)

    if tile is None:
        return np.nan

    row = int(round((lat_degree + 1 - lat) * 3600))
    col = int(round((lon - lon_degree) * 3600))

    row = max(0, min(3600, row))
    col = max(0, min(3600, col))

    value = int(tile[row, col])

    if value == -32768:
        return np.nan

    return value

selected["srtm_pixel_elevation_m"] = [
    get_elevation(lat, lon)
    for lat, lon in zip(
        selected["latitude"],
        selected["longitude"]
    )
]

selected.to_csv(output_file, index=False)

flood_pixels = selected[
    selected["flood_class"] == 3
].copy()

print("\nSRTM PIXEL-LEVEL ELEVATION VALIDATION")
print("=" * 75)

print("Total selected MODIS pixels:", len(selected))
print("Class-3 pixels:", len(flood_pixels))
print(
    "Class-3 pixels with SRTM elevation:",
    flood_pixels["srtm_pixel_elevation_m"].notna().sum()
)

print("\nCLASS-3 PIXEL ELEVATION SUMMARY")
print("-" * 75)

print(
    flood_pixels["srtm_pixel_elevation_m"]
    .describe()
    .round(2)
)

print("\nCLASS-3 PIXELS WITH ELEVATION")
print("-" * 75)

print(
    flood_pixels[[
        "latitude",
        "longitude",
        "cell_latitude",
        "cell_longitude",
        "elevation_mean_m",
        "srtm_pixel_elevation_m"
    ]].round(2).to_string(index=False)
)

print("\nOUTPUT SAVED:", output_file)
