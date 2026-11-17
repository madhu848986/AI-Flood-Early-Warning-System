import os
import glob
import numpy as np
import rasterio

from rasterio.merge import merge

INPUT_FOLDER = "datasets/raw/elevation"

OUTPUT_FOLDER = "datasets/processed/elevation"

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "koshi_elevation_30m.tif"
)

# Koshi study region
MIN_LON = 85.0
MAX_LON = 89.5
MIN_LAT = 25.0
MAX_LAT = 29.5

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Find all HGT elevation tiles
tile_files = glob.glob(
    os.path.join(INPUT_FOLDER, "*.hgt")
)

if not tile_files:
    raise FileNotFoundError("No HGT elevation tiles found.")

print("Elevation tiles found:", len(tile_files))

# Open elevation tiles
sources = [
    rasterio.open(tile)
    for tile in tile_files
]

try:
    # Merge and crop to the study region
    mosaic, transform = merge(
        sources,
        bounds=(
            MIN_LON,
            MIN_LAT,
            MAX_LON,
            MAX_LAT
        ),
        nodata=-32768
    )

    # Prepare GeoTIFF metadata
    metadata = sources[0].meta.copy()

    metadata.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": transform,
        "crs": sources[0].crs,
        "count": 1,
        "dtype": "int16",
        "nodata": -32768,
        "compress": "lzw"
    })

    # Save cropped elevation raster
    with rasterio.open(
        OUTPUT_FILE,
        "w",
        **metadata
    ) as destination:

        destination.write(mosaic)

finally:
    for source in sources:
        source.close()

# Validate output
with rasterio.open(OUTPUT_FILE) as dataset:

    elevation = dataset.read(1, masked=True)

    valid_values = elevation.compressed()

    print("\nElevation processing completed.")
    print("Output file:", OUTPUT_FILE)
    print("CRS:", dataset.crs)
    print("Raster width:", dataset.width)
    print("Raster height:", dataset.height)
    print("Valid elevation pixels:", len(valid_values))

    if len(valid_values) > 0:
        print("Minimum elevation (m):", valid_values.min())
        print("Maximum elevation (m):", valid_values.max())
        print("Mean elevation (m):", round(
            float(valid_values.mean()), 2
        ))
    else:
        raise ValueError("No valid elevation pixels found.")

print("\nSRTM elevation raster saved successfully.")