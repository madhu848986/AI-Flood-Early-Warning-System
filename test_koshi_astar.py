
import networkx as nx
import math

FILE = "datasets/processed/koshi_coordinate_road_graph.graphml"

print("Loading coordinate graph...", flush=True)

G = nx.read_graphml(FILE, node_type=str)

source = "J_45643"
target = "J_62200"

def heuristic(node, destination):
    x1 = float(G.nodes[node]["x"])
    y1 = float(G.nodes[node]["y"])

    x2 = float(G.nodes[destination]["x"])
    y2 = float(G.nodes[destination]["y"])

    return math.hypot(x2 - x1, y2 - y1)

print("Running A* algorithm...", flush=True)

try:
    path = nx.astar_path(
        G,
        source,
        target,
        heuristic=heuristic,
        weight="length_m"
    )

    distance = nx.path_weight(
        G,
        path,
        weight="length_m"
    )

    print("A* ROUTE FOUND")
    print("SOURCE:", source)
    print("DESTINATION:", target)
    print("PATH NODES:", len(path))
    print("TOTAL DISTANCE:", round(distance, 2), "metres")

except nx.NetworkXNoPath:
    print("NO ROUTE FOUND")

print("A* TEST COMPLETED")
