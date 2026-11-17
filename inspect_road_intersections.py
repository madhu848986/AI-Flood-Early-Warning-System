import geopandas as gpd
from shapely.strtree import STRtree

file = "datasets/processed/koshi_vehicle_roads.gpkg"

print("Loading roads...")

roads = gpd.read_file(file)

geometries = roads.geometry.to_numpy()

print("Total roads:", len(geometries))

print("Building spatial index...")

tree = STRtree(geometries)

intersection_pairs = 0
point_intersections = 0
overlapping_intersections = 0

for i, geometry in enumerate(geometries):

    candidates = tree.query(geometry)

    for j in candidates:

        j = int(j)

        if j <= i:
            continue

        other = geometries[j]

        if not geometry.intersects(other):
            continue

        intersection_pairs += 1

        result = geometry.intersection(other)

        if result.geom_type == "Point":
            point_intersections += 1

        elif result.geom_type == "MultiPoint":
            point_intersections += len(result.geoms)

        elif result.geom_type in [
            "LineString", "MultiLineString"
        ]:
            overlapping_intersections += 1

print("\nROAD INTERSECTION ANALYSIS")
print("Intersecting road pairs:", intersection_pairs)
print("Point intersections:", point_intersections)
print("Overlapping road pairs:", overlapping_intersections)