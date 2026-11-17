import geopandas as gpd
from shapely.strtree import STRtree

input_file = "datasets/processed/koshi_vehicle_roads_grade.gpkg"
output_file = "datasets/processed/koshi_road_intersection_points.gpkg"

print("Loading grade-aware road network...")
roads = gpd.read_file(input_file).reset_index(drop=True)

geometries = roads.geometry.to_numpy()
layers = roads["layer"].to_numpy()
bridges = roads["bridge"].to_numpy()
tunnels = roads["tunnel"].to_numpy()
fords = roads["ford"].to_numpy()

osm_ids = roads["osm_id"].astype(str).to_numpy()

print("Building spatial index...")
tree = STRtree(geometries)

records = []

endpoint_endpoint = 0
endpoint_interior = 0
interior_interior = 0
different_layer = 0
grade_separated = 0
ford_review = 0

tolerance = 0.5


def extract_points(geometry):
    if geometry.is_empty:
        return []

    if geometry.geom_type == "Point":
        return [geometry]

    if geometry.geom_type == "MultiPoint":
        return list(geometry.geoms)

    if geometry.geom_type == "GeometryCollection":
        points = []
        for item in geometry.geoms:
            points.extend(extract_points(item))
        return points

    return []


print("Finding road intersections...")

for i, geometry in enumerate(geometries):

    candidates = tree.query(geometry)

    for j in candidates:

        j = int(j)

        if j <= i:
            continue

        other = geometries[j]

        if not geometry.intersects(other):
            continue

        intersection = geometry.intersection(other)
        points = extract_points(intersection)

        for point in points:

            d1 = point.distance(geometry.boundary)
            d2 = point.distance(other.boundary)

            first_endpoint = d1 <= tolerance
            second_endpoint = d2 <= tolerance

            if first_endpoint and second_endpoint:
                connection_type = "endpoint_endpoint"
                endpoint_endpoint += 1

            elif first_endpoint or second_endpoint:
                connection_type = "endpoint_interior"
                endpoint_interior += 1

            else:
                connection_type = "interior_interior"
                interior_interior += 1

            same_layer = layers[i] == layers[j]

            has_grade_tags = (
                bridges[i] or bridges[j]
                or tunnels[i] or tunnels[j]
            )

            has_ford = fords[i] or fords[j]

            if not same_layer:
                decision = "review"
                reason = "different_layers"
                different_layer += 1

            elif has_grade_tags:
                decision = "review"
                reason = "bridge_or_tunnel"
                grade_separated += 1

            elif has_ford:
                decision = "ford_review"
                reason = "ford_crossing"
                ford_review += 1

            elif connection_type == "endpoint_endpoint":
                decision = "endpoint_candidate"
                reason = "shared_endpoints"

            else:
                decision = "at_grade_candidate"
                reason = "same_layer_no_grade_tags"

            records.append({
                "road_i": i,
                "road_j": j,
                "osm_id_i": osm_ids[i],
                "osm_id_j": osm_ids[j],
                "layer_i": int(layers[i]),
                "layer_j": int(layers[j]),
                "connection_type": connection_type,
                "decision": decision,
                "reason": reason,
                "geometry": point
            })


print("\nCreating intersection dataset...")

if records:

    result = gpd.GeoDataFrame(
        records,
        geometry="geometry",
        crs=roads.crs
    )

    result.to_file(output_file, driver="GPKG")

    print("\nINTERSECTION POINT RESULTS")
    print("Total intersection points:", len(result))

    print("\nConnection type:")
    print(result["connection_type"].value_counts())

    print("\nDecision:")
    print(result["decision"].value_counts())

    print("\nReview reason:")
    print(result["reason"].value_counts())

    print("\nSaved:", output_file)

else:
    print("No point intersections found.")

print("\nINTERSECTION POINT GENERATION COMPLETED")