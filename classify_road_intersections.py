import geopandas as gpd
from shapely.strtree import STRtree

file = "datasets/processed/koshi_vehicle_roads_grade.gpkg"

print("Loading grade-aware roads...")
roads = gpd.read_file(file)

geometries = roads.geometry.to_numpy()
layers = roads["layer"].to_numpy()
bridges = roads["bridge"].to_numpy()
tunnels = roads["tunnel"].to_numpy()

tree = STRtree(geometries)

endpoint_endpoint = 0
endpoint_interior = 0
interior_interior = 0

different_layer = 0
bridge_tunnel_crossings = 0
potential_connections = 0

tolerance = 0.5

print("Classifying grade-aware intersections...")

for i, geometry in enumerate(geometries):

    candidates = tree.query(geometry)

    for j in candidates:

        j = int(j)

        if j <= i:
            continue

        other = geometries[j]

        if not geometry.intersects(other):
            continue

        result = geometry.intersection(other)

        if result.geom_type == "Point":
            points = [result]

        elif result.geom_type == "MultiPoint":
            points = list(result.geoms)

        else:
            continue

        for point in points:

            if layers[i] != layers[j]:
                different_layer += 1
                continue

            if bridges[i] or bridges[j] or tunnels[i] or tunnels[j]:
                bridge_tunnel_crossings += 1
                continue

            d1 = point.distance(geometry.boundary)
            d2 = point.distance(other.boundary)

            first_endpoint = d1 <= tolerance
            second_endpoint = d2 <= tolerance

            if first_endpoint and second_endpoint:
                endpoint_endpoint += 1

            elif first_endpoint or second_endpoint:
                endpoint_interior += 1

            else:
                interior_interior += 1

            potential_connections += 1

print("\nGRADE-AWARE INTERSECTION RESULTS")
print("Potential at-grade connections:", potential_connections)
print("Endpoint-to-endpoint:", endpoint_endpoint)
print("Endpoint-to-interior:", endpoint_interior)
print("Interior-to-interior:", interior_interior)
print("Different-layer crossings:", different_layer)
print("Bridge/tunnel crossings excluded:", bridge_tunnel_crossings)

print("\nINTERSECTION ANALYSIS COMPLETED")