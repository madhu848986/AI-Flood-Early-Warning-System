from pathlib import Path
from pyhdf.SD import SD, SDC

file_path = Path(
    "datasets/raw/flood_events/nasa_flood_maps/"
    "MCDWD_L3.A2021286.h26v06.061.2025278052519.hdf"
)

hdf = SD(str(file_path), SDC.READ)

print("NASA FLOOD FILE METADATA")
print("=" * 50)

print("\nGLOBAL ATTRIBUTES:")
for key, value in hdf.attributes().items():
    print(f"{key}: {value}")

print("\nDATASET DETAILS:")
for name, info in hdf.datasets().items():
    print(f"\nDataset: {name}")
    print("Dimensions:", info[1])
    print("Shape:", info[2])
    print("Data type:", info[3])

    dataset = hdf.select(name)
    for key, value in dataset.attributes().items():
        print(f"  {key}: {value}")

hdf.end()