from pathlib import Path
from pyhdf.SD import SD, SDC

file_path = Path(
    "datasets/raw/flood_events/nasa_flood_maps/"
    "MCDWD_L3.A2021286.h26v06.061.2025278052519.hdf"
)

if not file_path.exists():
    print("ERROR: HDF file not found.")
    raise SystemExit

hdf = SD(str(file_path), SDC.READ)

print("GLOBAL ATTRIBUTES")
print("=" * 60)

for name, value in hdf.attributes().items():
    print(f"\n{name}:")

    if isinstance(value, str):
        print(value[:2000])
    else:
        print(value)

hdf.end()