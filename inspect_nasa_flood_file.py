
from pathlib import Path
from pyhdf.SD import SD, SDC

file_path = Path(
    "datasets/raw/flood_events/nasa_flood_maps/"
    "MCDWD_L3.A2021286.h26v06.061.2025278052519.hdf"
)

print("NASA FLOOD LAYER INSPECTION")
print("=" * 45)

if not file_path.exists():
    print("ERROR: NASA file not found.")
else:
    hdf = SD(str(file_path), SDC.READ)

    print("\nGlobal attributes:")
    for name, value in hdf.attributes().items():
        print(f"{name}: {value}")

    datasets = hdf.datasets()

    print("\nTotal data layers:", len(datasets))
    print("\nDATA LAYERS")
    print("=" * 45)

    for name, details in datasets.items():
        print("\nLayer name:", name)
        print("Dimensions:", details[1])
        print("Data type:", details[3])

        layer = hdf.select(name)
        print("Shape:", layer.info()[2])

        attributes = layer.attributes()
        if attributes:
            print("Attributes:")
            for attr_name, attr_value in attributes.items():
                print(f"  {attr_name}: {attr_value}")

    hdf.end()
    print("\nInspection completed successfully.")
