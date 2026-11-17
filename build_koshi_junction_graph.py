
import sqlite3
import networkx as nx
import shapely
from shapely.ops import substring
from collections import defaultdict

ROAD_FILE = "datasets/processed/koshi_vehicle_roads_grade.gpkg"
JUNCTION_FILE = "datasets/processed/koshi_unique_road_junctions.gpkg"
OUTPUT_FILE = "datasets/processed/koshi_junction_road_graph.graphml"

def read_geometry(data):
    envelope = (data[3] >> 1) & 7
    offset = 8

    if envelope == 1:
        offset += 32
    elif envelope in (2, 3):
        offset += 48
    elif envelope == 4:
        offset += 64

    return shapely.from_wkb(data[offset:])

print("Reading junction references...", flush=True)

junction_db = sqlite3.connect(JUNCTION_FILE)
road_db = sqlite3.connect(ROAD_FILE)

road_junctions = defaultdict(list)

junction_rows = junction_db.execute(
    "SELECT junction_id, road_indices, geom "
    "FROM koshi_unique_road_junctions"
)

junction_count = 0

for junction_id, road_indices, geometry in junction_rows:
    point = read_geometry(geometry)

    for reference in road_indices.split(","):
        road_fid = int(reference) + 1
        road_junctions[road_fid].append(
            (junction_id, point)
        )

    junction_count += 1

print("Junctions loaded:", junction_count, flush=True)
print("Reading roads and building graph...", flush=True)

G = nx.MultiDiGraph()
road_cursor = road_db.execute(
    "SELECT fid, geom, osm_id, name, highway, oneway, "
    "length_m, layer, bridge, tunnel, ford "
    "FROM koshi_vehicle_roads_grade"
)

road_count = 0
segment_count = 0
unmatched_count = 0

def endpoint_node(x, y):
    return "E_" + str(round(x, 2)) + "_" + str(round(y, 2))

for row in road_cursor:
    (
        fid, geometry, osm_id, name, highway, oneway,
        length_m, layer, bridge, tunnel, ford
    ) = row

    line = read_geometry(geometry)

    if line.is_empty or line.length == 0:
        continue

    positions = []

    for junction_id, point in road_junctions.get(fid, []):
        distance = line.project(point)
        projected_point = line.interpolate(distance)

        if point.distance(projected_point) <= 1:
            positions.append((distance, junction_id))
        else:
            unmatched_count += 1

    positions.sort()

    unique_positions = []

    for distance, junction_id in positions:
        if unique_positions and abs(
            distance - unique_positions[-1][0]
        ) < 0.01:
            continue

        unique_positions.append((distance, junction_id))

    boundaries = [(0.0, None)] + unique_positions
    boundaries.append((line.length, None))

    start_point = line.interpolate(0)

    if unique_positions and unique_positions[0][0] <= 1:
        start_node = "J_" + str(unique_positions[0][1])
    else:
        start_node = endpoint_node(
            start_point.x, start_point.y
        )

    for index in range(len(boundaries) - 1):
        start_distance, start_junction = boundaries[index]
        end_distance, end_junction = boundaries[index + 1]

        if end_distance - start_distance < 0.01:
            continue

        segment = substring(
            line, start_distance, end_distance
        )

        if segment.is_empty or segment.length == 0:
            continue

        if start_junction is not None:
            u = "J_" + str(start_junction)
        elif index == 0:
            u = start_node
        else:
            u = "J_" + str(boundaries[index][1])

        if end_junction is not None:
            v = "J_" + str(end_junction)
        else:
            end_point = line.interpolate(end_distance)
            v = endpoint_node(end_point.x, end_point.y)

        if u == v:
            continue

        attributes = {
            "road_fid": str(fid),
            "osm_id": str(osm_id or ""),
            "name": str(name or ""),
            "highway": str(highway or ""),
            "length_m": float(segment.length),
            "layer": int(layer or 0),
            "bridge": str(bridge),
            "tunnel": str(tunnel),
            "ford": str(ford)
        }

        direction = str(oneway or "").lower()

        if direction in ("-1", "reverse"):
            G.add_edge(v, u, **attributes)
        elif direction in ("yes", "1", "true"):
            G.add_edge(u, v, **attributes)
        else:
            G.add_edge(u, v, **attributes)
            G.add_edge(v, u, **attributes)

        segment_count += 1

        start_node = v

    road_count += 1

    if road_count % 10000 == 0:
        print(
            "Roads processed:", road_count,
            "| Segments:", segment_count,
            flush=True
        )

print("Saving graph...", flush=True)

nx.write_graphml(G, OUTPUT_FILE)

print("GRAPH BUILD COMPLETE")
print("Roads processed:", road_count)
print("Segments created:", segment_count)
print("Nodes:", G.number_of_nodes())
print("Directed edges:", G.number_of_edges())
print("Unmatched junction references:", unmatched_count)
print("Output:", OUTPUT_FILE)

road_db.close()
junction_db.close()
