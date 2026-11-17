import pandas as pd
import numpy as np

flood_path = "datasets/processed/koshi_nasa_flood_pixels.csv"

flood = pd.read_csv(flood_path)

cell_step = 0.1

# Rainfall grid boundaries begin at latitude 25.0 and longitude 85.0.
flood["cell_row"] = np.floor(
    (flood["latitude"] - 25.0) / cell_step
).astype(int)

flood["cell_col"] = np.floor(
    (flood["longitude"] - 85.0) / cell_step
).astype(int)

cell_counts = flood.groupby(["cell_row", "cell_col"]).size()

print("CELL ASSIGNMENT VALIDATION")
print("=" * 40)
print("MODIS pixels:", len(flood))
print("Unique assigned cells:", len(cell_counts))

print("\nPixel count per cell:")
print(cell_counts.describe())

print("\nPixel counts frequency:")
print(cell_counts.value_counts().sort_index())

print("\nCells with unexpected pixel counts:")
print(cell_counts[cell_counts != 2304].head(20))