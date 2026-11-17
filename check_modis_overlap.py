import pandas as pd

rainfall_path = (
    "datasets/processed/"
    "koshi_rainfall_october_13_14_2021.csv"
)

flood_path = (
    "datasets/processed/koshi_nasa_flood_pixels.csv"
)

rainfall = pd.read_csv(rainfall_path)
flood = pd.read_csv(flood_path)

lat_step = 0.1
lon_step = 0.1

# Approximate rainfall-cell boundaries, assuming coordinates are centers.
rain_lat_min = rainfall["latitude"].min() - lat_step / 2
rain_lat_max = rainfall["latitude"].max() + lat_step / 2
rain_lon_min = rainfall["longitude"].min() - lon_step / 2
rain_lon_max = rainfall["longitude"].max() + lon_step / 2

print("GEOGRAPHIC OVERLAP CHECK")
print("=" * 45)

print("\nRainfall grid boundaries (approximate):")
print("Latitude:", rain_lat_min, "to", rain_lat_max)
print("Longitude:", rain_lon_min, "to", rain_lon_max)

print("\nExtracted MODIS pixel-center bounds:")
print("Latitude:", flood["latitude"].min(),
      "to", flood["latitude"].max())
print("Longitude:", flood["longitude"].min(),
      "to", flood["longitude"].max())

inside = flood[
    flood["latitude"].between(rain_lat_min, rain_lat_max)
    & flood["longitude"].between(rain_lon_min, rain_lon_max)
]

print("\nMODIS pixels inside rainfall-grid bounds:", len(inside))
print("Total extracted MODIS pixels:", len(flood))
print("Pixels outside rainfall-grid bounds:", len(flood) - len(inside))

print("\nMODIS flood classes inside overlap:")
print(inside["flood_class"].value_counts().sort_index())