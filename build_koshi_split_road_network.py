
import geopandas as gpd
import pandas as pd
from collections import defaultdict
from shapely.geometry import LineString
from shapely.ops import substring

roads_file = "datasets/processed/koshi_vehicle_roads_grade.gpkg"
junctions_file = "datasets/processed/koshi_unique_road_junctions.gpkg"
output_file = "datasets/processed/koshi_split_road_segments.gpkg"

print("Loading road network...")
roads = gpd.read_file(roads_file).reset_index(drop=True)

print("Loading candidate junctions...")
junctions = gpd.read_file(junctions_file)

road_junctions = defaultdict(list)

for row in junctions.itertuples():
    point = row.geometry
    road_ids = map(int, row.road_indices.split(","))

    for road_id in road_ids:
        if 0 <= road_id < len(roads):
            road_junctions[road_id].append(point)

print("Preparing road segments...")

segments = []
segment_id = 0

for road_id, row in enumerate(roads.itertuples()):
    line = row.geometry

    if line is None or line.is_empty:
        continue

    if line.geom_type != "LineString":
        continue

    length = line.length

    if length <= 0:
        continue

    distances = []

    for point in road_junctions.get(road_id, []):
        distance = line.project(point)

        if line.interpolate(distance).distance(point) <= 0.5:
            if 0.01 < distance < length - 0.01:
                distances.append(distance)

    distances.sort()

    unique_distances = []

    for distance in distances:
        if not unique_distances or distance - unique_distances[-1] > 0.05:
            unique_distances.append(distance)

    boundaries = [0.0] + unique_distances + [length]

    for start, end in zip(boundaries[:-1], boundaries[1:]):
        if end - start <= 0.1:
            continue

        part = substring(line, start, end)

        if part is None or part.is_empty or part.geom_type != "LineString":
            continue

        if part.length <= 0:
            continue

        attributes = row._asdict()
        attributes.pop("Index", None)
        attributes.pop("geometry", None)

        attributes["road_index"] = road_id
        attributes["segment_id"] = segment_id
        attributes["length_m"] = part.length
        attributes["start_node"] = (
            round(part.coords[0][0], 2),
            round(part.coords[0][1], 2)
        )
        attributes["end_node"] = (
            round(part.coords[-1][0], 2),
            round(part.coords[-1][1], 2)
        )

        attributes["geometry"] = part
        segments.append(attributes)

        segment_id += 1

    if road_id > 0 and road_id % 20000 == 0:
        print("Processed roads:", road_id, "/", len(roads))

print("Creating output dataset...")

result = gpd.GeoDataFrame(
    segments,
    geometry="geometry",
    crs=roads.crs
)

result.to_file(output_file, driver="GPKG")

print("\nROAD SPLITTING COMPLETED")
print("Original roads:", len(roads))
print("Output road segments:", len(result))
print("Roads without eligible junction references:",
      len(roads) - len(road_junctions))
print("Invalid geometries:", (~result.geometry.is_valid).sum())
print("Empty geometries:", result.geometry.is_empty.sum())
print("Total segment length (km):", round(result.length.sum() / 1000, 2))
print("Output:", output_file)
