import geopandas as gpd
import numpy as np

file = "datasets/processed/koshi_vehicle_roads_grade.gpkg"

print("Loading roads...")
roads = gpd.read_file(file)

vertex_counts = roads.geometry.apply(
    lambda geometry: len(geometry.coords)
)

print("\nROAD VERTEX ANALYSIS")
print("Total roads:", len(roads))
print("Minimum vertices:", vertex_counts.min())
print("Maximum vertices:", vertex_counts.max())
print("Average vertices:", round(vertex_counts.mean(), 2))
print("Median vertices:", vertex_counts.median())

print("\nVERTEX COUNT DISTRIBUTION")
print(vertex_counts.describe())

print("\nROADS WITH MORE THAN 2 VERTICES:")
print((vertex_counts > 2).sum())