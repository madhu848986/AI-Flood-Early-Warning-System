import numpy as np

north = 30.0
south = 20.0
west = 80.0
east = 90.0

rows = 4800
cols = 4800

lat_step = (north - south) / rows
lon_step = (east - west) / cols

latitudes = north - (np.arange(rows) + 0.5) * lat_step
longitudes = west + (np.arange(cols) + 0.5) * lon_step

print("MODIS GRID SPACING CHECK")
print("=" * 40)

print(f"Latitude spacing: {lat_step:.12f} degrees")
print(f"Longitude spacing: {lon_step:.12f} degrees")

print("\nFirst pixel center:")
print(f"Latitude: {latitudes[0]:.9f}")
print(f"Longitude: {longitudes[0]:.9f}")

print("\nLast pixel center:")
print(f"Latitude: {latitudes[-1]:.9f}")
print(f"Longitude: {longitudes[-1]:.9f}")

print("\nGrid dimensions:", rows, "x", cols)
print("Grid cells:", rows * cols)