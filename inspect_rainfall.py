
import h5netcdf
import os

file_path = os.path.join(
    "datasets", "raw", "gpm_historical",
    "3B-DAY.MS.MRG.3IMERG.20200901-S000000-E235959.V07B.nc4"
)

print("Inspecting rainfall file...")

try:
    with h5netcdf.File(
        file_path, mode="r", backend="pyfive"
    ) as f:
        print("\n--- DIMENSIONS ---")
        print(dict(f.dimensions))

        print("\n--- VARIABLES ---")
        for name, variable in f.variables.items():
            print(name, variable.shape)
            print("Attributes:", dict(variable.attrs))

        print("\n--- GROUPS ---")
        print(list(f.groups.keys()))

    print("\nInspection completed.")

except Exception as e:
    print("Error:", repr(e))
