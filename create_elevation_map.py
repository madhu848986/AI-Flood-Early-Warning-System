
import os
import numpy as np
import matplotlib.pyplot as plt

folder = os.path.join("datasets", "raw", "elevation")
output_folder = os.path.join("datasets", "processed")
os.makedirs(output_folder, exist_ok=True)

tiles = {}

for filename in os.listdir(folder):
    if not filename.lower().endswith(".hgt"):
        continue

    name = filename[:-4]

    # Expected name: N25E085
    lat = int(name[1:3])
    lon = int(name[4:7])

    path = os.path.join(folder, filename)
    data = np.fromfile(path, dtype=">i2")

    size = int(np.sqrt(data.size))

    if size * size != data.size:
        print("Skipping invalid tile:", filename)
        continue

    tiles[(lat, lon)] = data.reshape(size, size)

if not tiles:
    raise RuntimeError("No valid HGT tiles found.")

min_lat = min(lat for lat, lon in tiles)
max_lat = max(lat for lat, lon in tiles)
min_lon = min(lon for lat, lon in tiles)
max_lon = max(lon for lat, lon in tiles)

tile_size = next(iter(tiles.values())).shape[0]
rows = (max_lat - min_lat + 1) * (tile_size - 1) + 1
cols = (max_lon - min_lon + 1) * (tile_size - 1) + 1

mosaic = np.full((rows, cols), -32768, dtype=np.int16)

for (lat, lon), data in tiles.items():
    r = (max_lat - lat) * (tile_size - 1)
    c = (lon - min_lon) * (tile_size - 1)
    mosaic[r:r + tile_size, c:c + tile_size] = data


valid = mosaic != -32768

# Reduce resolution for visualization only.
# Original elevation tiles remain unchanged.
step = 12
small = mosaic[::step, ::step].astype(np.float32)
small[small == -32768] = np.nan

plt.figure(figsize=(10, 7))

image = plt.imshow(
    small,
    extent=[min_lon, max_lon + 1, min_lat, max_lat + 1],
    origin="upper",
    aspect="auto",
    interpolation="nearest"
)

plt.colorbar(image, label="Elevation (metres)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("SRTM Elevation — Koshi Study Area")
plt.tight_layout()

output_path = os.path.join(
    output_folder, "koshi_elevation_map.png"
)

plt.savefig(output_path, dpi=150)
plt.close()

valid_values = mosaic[mosaic != -32768]

print("Tiles loaded:", len(tiles))
print("Elevation minimum:", int(valid_values.min()), "m")
print("Elevation maximum:", int(valid_values.max()), "m")
print("Map saved to:", output_path)
