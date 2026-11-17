
from pathlib import Path
import h5netcdf

folder = Path("datasets/raw/gpm_historical/october_2021")
files = sorted(folder.glob("*.nc4"))

print("Checking", len(files), "files")

for file in files:
    print("\nFILE:", file.name)

    try:
        with h5netcdf.File(file, mode="r", backend="pyfive") as data:
            print("Opened: OK")
            print("Variables:", list(data.variables.keys())[:15])
            print("Dimensions:", dict(data.dimensions))

    except Exception as error:
        print("FAILED:", error)
