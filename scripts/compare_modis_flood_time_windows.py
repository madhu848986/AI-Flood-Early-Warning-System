
import pandas as pd
import numpy as np
from pyhdf.SD import SD, SDC

hdf_file = (
    "datasets/raw/flood_events/nasa_flood_maps/"
    "MCDWD_L3.A2021286.h26v06.061.2025278052519.hdf"
)

pixel_file = (
    "datasets/processed/"
    "koshi_high_altitude_modis_pixels_with_srtm.csv"
)

output_file = (
    "datasets/processed/"
    "koshi_high_altitude_modis_temporal_comparison.csv"
)

hdf = SD(hdf_file, SDC.READ)
pixels = pd.read_csv(pixel_file)

high_pixels = pixels[pixels["flood_class"] == 3].copy()

layers = [
    "FloodCS_1Day_250m",
    "Flood_2Day_250m",
    "Flood_3Day_250m"
]
def get_modis_value(layer, lat, lon):
    data = hdf.select(layer)[:]

    row = int(round((30 - lat) * 480 - 0.5))
    col = int(round((lon - 80) * 480 - 0.5))

    row = max(0, min(data.shape[0] - 1, row))
    col = max(0, min(data.shape[1] - 1, col))

    return int(data[row, col])

for layer in layers:
    high_pixels[layer] = [
        get_modis_value(layer, lat, lon)
        for lat, lon in zip(
            high_pixels["latitude"],
            high_pixels["longitude"]
        )
    ]

hdf.end()

print("\nMODIS TEMPORAL COMPARISON")
print("=" * 65)

for layer in layers:
    print(f"\n{layer}")
    print(high_pixels[layer].value_counts().sort_index())

print("\nCLASS-3 PIXEL COMPARISON")
print("-" * 65)

for layer in layers:
    print(
        layer,
        "class-3 detections:",
        int((high_pixels[layer] == 3).sum())
    )

high_pixels.to_csv(output_file, index=False)

print("\nOutput saved:", output_file)
