
import sqlite3
import networkx as nx
import shapely

GRAPH_FILE = "datasets/processed/koshi_junction_road_graph.graphml"
JUNCTION_FILE = "datasets/processed/koshi_unique_road_junctions.gpkg"
OUTPUT_FILE = "datasets/processed/koshi_coordinate_road_graph.graphml"

print("Loading graph...", flush=True)
G = nx.read_graphml(GRAPH_FILE, node_type=str)

print("Reading junction coordinates...", flush=True)

db = sqlite3.connect(JUNCTION_FILE)

rows = db.execute(
    "SELECT junction_id, geom FROM koshi_unique_road_junctions"
)

junction_coordinates = {}

for junction_id, geometry in rows:
    point = shapely.from_wkb(geometry[8:])
    junction_coordinates["J_" + str(junction_id)] = (
        point.x, point.y
    )

db.close()

print("Adding node coordinates...", flush=True)

matched = 0
missing = 0

for node in G.nodes():

    if node.startswith("J_"):
        coordinates = junction_coordinates.get(node)

        if coordinates is not None:
            G.nodes[node]["x"] = float(coordinates[0])
            G.nodes[node]["y"] = float(coordinates[1])
            matched += 1
        else:
            missing += 1

    elif node.startswith("E_"):
        parts = node.split("_")

        G.nodes[node]["x"] = float(parts[1])
        G.nodes[node]["y"] = float(parts[2])
        matched += 1

print("Saving coordinate graph...", flush=True)

nx.write_graphml(G, OUTPUT_FILE)

print("COORDINATE ENRICHMENT COMPLETED")
print("TOTAL NODES:", G.number_of_nodes())
print("NODES WITH COORDINATES:", matched)
print("MISSING JUNCTION COORDINATES:", missing)
print("OUTPUT:", OUTPUT_FILE)
