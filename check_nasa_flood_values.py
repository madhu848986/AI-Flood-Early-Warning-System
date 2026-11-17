
from pathlib import Path
from collections import Counter
from pyhdf.SD import SD, SDC
import numpy as np

file_path = Path(
    "datasets/raw/flood_events/nasa_flood_maps/"
    "MCDWD_L3.A2021286.h26v06.061.2025278052519.hdf"
)

if not file_path.exists():
    print("ERROR: NASA flood file not found.")
else:
    hdf = SD(str(file_path), SDC.READ)

    layers = [
        "FloodCS_1Day_250m",
        "Flood_1Day_250m"
    ]

    meanings = {
        0: "No water",
        1: "Water matching reference water",
        2: "Recurring/seasonal flood",
        3: "Unusual flood",
        255: "Insufficient data"
    }

    for layer_name in layers:
        print("\n" + "=" * 45)
        print("LAYER:", layer_name)
        print("=" * 45)

        pixels = np.asarray(hdf.select(layer_name).get())
        values, counts = np.unique(pixels, return_counts=True)

        total_pixels = pixels.size
        count_dict = dict(zip(values.tolist(), counts.tolist()))

        for value in [0, 1, 2, 3, 255]:
            count = count_dict.get(value, 0)
            percentage = count / total_pixels * 100

            print(
                f"Value {value} - {meanings[value]}: "
                f"{count:,} pixels ({percentage:.2f}%)"
            )

        valid_pixels = total_pixels - count_dict.get(255, 0)
        unusual_flood = count_dict.get(3, 0)

        print("\nTotal pixels:", f"{total_pixels:,}")
        print("Valid pixels:", f"{valid_pixels:,}")
        print("Unusual-flood pixels:", f"{unusual_flood:,}")

    hdf.end()
    print("\nFlood-value inspection completed.")
