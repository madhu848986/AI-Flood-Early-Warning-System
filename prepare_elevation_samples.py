
import os
import numpy as np
import pandas as pd

folder = os.path.join("datasets", "raw", "elevation")
output_folder = os.path.join("datasets", "processed")
os.makedirs(output_folder, exist_ok=True)

records = []
step = 30  # Sample every 120th pixel (~1.2 km)

for filename in sorted(os.listdir(folder)):
    if not filename.lower().endswith(".hgt"):
        continue

    name = filename[:-4]
    lat0 = int(name[1:3])
    lon0 = int(name[4:7])

    path = os.path.join(folder, filename)
    data = np.fromfile(path, dtype=">i2").reshape(3601, 3601)

    sampled = data[::step, ::step]

    for row in range(sampled.shape[0]):
        for col in range(sampled.shape[1]):
            elevation = int(sampled[row, col])

            if elevation == -32768:
                continue

            latitude = lat0 + 1 - (row * step / 3600)
            longitude = lon0 + (col * step / 3600)

            records.append({
                "latitude": round(latitude, 5),
                "longitude": round(longitude, 5),
                "elevation_m": elevation
            })

df = pd.DataFrame(records)

output_path = os.path.join(
    output_folder, "koshi_elevation_samples.csv"
)
df.to_csv(output_path, index=False)

print("Elevation samples:", len(df))
print("Minimum elevation:", df["elevation_m"].min(), "m")
print("Maximum elevation:", df["elevation_m"].max(), "m")
print("Saved to:", output_path)
