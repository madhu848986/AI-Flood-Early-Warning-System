
import os
import struct
import numpy as np

folder = os.path.join("datasets", "raw", "elevation")

files = sorted(
    name for name in os.listdir(folder)
    if name.lower().endswith(".hgt")
)

print("Total elevation tiles:", len(files))

for filename in files:
    path = os.path.join(folder, filename)

    try:
        file_size = os.path.getsize(path)

        with open(path, "rb") as f:
            header = f.read(2)

        # Standard SRTM HGT files contain signed 16-bit
        # big-endian elevation values.
        samples = int((file_size // 2) ** 0.5)

        if file_size % 2 != 0 or samples * samples * 2 != file_size:
            print(filename, "| Unexpected file size:", file_size)
            continue

        elevation = np.fromfile(path, dtype=">i2").reshape(
            samples, samples
        )

        valid = elevation[elevation != -32768]

        if valid.size:
            print(
                filename,
                "| shape:", elevation.shape,
                "| min:", int(valid.min()), "m",
                "| max:", int(valid.max()), "m",
                "| mean:", round(float(valid.mean()), 2), "m"
            )
        else:
            print(filename, "| No valid elevation values")

    except Exception as error:
        print(filename, "| ERROR:", error)
