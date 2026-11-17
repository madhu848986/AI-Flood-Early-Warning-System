import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

file = "datasets/processed/koshi_vehicle_roads.gpkg"

print("Loading roads...")

roads = gpd.read_file(file)

endpoints = []

for geometry in roads.geometry:
    coordinates = list(geometry.coords)

    endpoints.append(coordinates[0])
    endpoints.append(coordinates[-1])

points = np.array(endpoints)

print("Total endpoints:", len(points))

print("Building spatial index...")

tree = cKDTree(points)

distances, indices = tree.query(points, k=2)

nearest_distances = distances[:, 1]

print("\nNEAREST ENDPOINT GAP STATISTICS")
print("Minimum:", round(nearest_distances.min(), 3), "m")
print("Median:", round(np.median(nearest_distances), 3), "m")
print("Mean:", round(nearest_distances.mean(), 3), "m")

print("\nENDPOINT GAP COUNTS")

for tolerance in [0.1, 0.5, 1, 2, 5, 10]:
    count = np.sum(nearest_distances <= tolerance)

    print(
        f"Within {tolerance} m:",
        count,
        f"({count / len(points) * 100:.2f}%)"
    )