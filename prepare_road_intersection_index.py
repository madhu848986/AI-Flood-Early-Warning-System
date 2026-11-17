import geopandas as gpd
import numpy as np
from shapely.strtree import STRtree

input_file = "datasets/processed/koshi_vehicle_roads_grade.gpkg"

print("Loading road network...")

roads = gpd.read_file(input_file)

geometries = roads.geometry.to_numpy()

print("Building spatial index...")

tree = STRtree(geometries)

print("\nROAD INTERSECTION INDEX")
print("Total roads:", len(roads))
print("Spatial index created:", tree is not None)

sample = geometries[:5]

print("\nTesting spatial queries...")

for i, geometry in enumerate(sample):
    candidates = tree.query(geometry)
    print(f"Road {i + 1}: {len(candidates)} candidate roads")

print("\nROAD INTERSECTION INDEX PREPARATION COMPLETED")