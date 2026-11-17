import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

file = "datasets/processed/koshi_vehicle_roads.gpkg"

print("Loading roads...")

roads = gpd.read_file(file)

points = []
road_ids = []

for road_id, geometry in enumerate(roads.geometry):

    coordinates = list(geometry.coords)

    points.append(coordinates[0])
    road_ids.append(road_id)

    points.append(coordinates[-1])
    road_ids.append(road_id)

points = np.array(points)
road_ids = np.array(road_ids)

print("Total endpoints:", len(points))

tree = cKDTree(points)

distances, indices = tree.query(points, k=10)

nearest_other_road = []

for i in range(len(points)):

    valid = road_ids[indices[i]] != road_ids[i]

    if valid.any():
        nearest_other_road.append(distances[i][valid][0])

nearest_other_road = np.array(nearest_other_road)

print("\nDIFFERENT-ROAD ENDPOINT GAP STATISTICS")
print("Count:", len(nearest_other_road))
print("Minimum:", round(nearest_other_road.min(), 3), "m")
print("Median:", round(np.median(nearest_other_road), 3), "m")
print("Mean:", round(nearest_other_road.mean(), 3), "m")

print("\nDISTANCE COUNTS")

for tolerance in [0.1, 0.5, 1, 2, 5, 10]:
    count = np.sum(nearest_other_road <= tolerance)

    print(
        f"Within {tolerance} m:",
        count,
        f"({count / len(nearest_other_road) * 100:.2f}%)"
    )