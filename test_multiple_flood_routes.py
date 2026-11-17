
import networkx as nx
import math

FILE = "datasets/processed/koshi_bilinear_flood_risk_road_graph.graphml"
LAMBDA = 20.0

print("Loading road graph...", flush=True)

G = nx.read_graphml(FILE, node_type=str)

print("Finding largest connected component...", flush=True)

components = list(nx.weakly_connected_components(G))
largest = max(components, key=len)

H = G.subgraph(largest).copy()

print("Largest component nodes:", len(H), flush=True)

print("Building distance and flood-cost graphs...", flush=True)

D = nx.DiGraph()
F = nx.DiGraph()

for u, v, key, data in H.edges(keys=True, data=True):

    length = float(data["length_m"])
    probability = float(data["flood_probability"])

    flood_cost = length * (1 + LAMBDA * probability)

    if not D.has_edge(u, v) or length < D[u][v]["cost"]:
        D.add_edge(u, v, cost=length, length=length,
                   probability=probability)

    if not F.has_edge(u, v) or flood_cost < F[u][v]["cost"]:
        F.add_edge(u, v, cost=flood_cost, length=length,
                   probability=probability)

print("Selecting geographically separated nodes...", flush=True)

nodes = list(H.nodes(data=True))

west = min(nodes, key=lambda item: float(item[1]["x"]))[0]
east = max(nodes, key=lambda item: float(item[1]["x"]))[0]
south = min(nodes, key=lambda item: float(item[1]["y"]))[0]
north = max(nodes, key=lambda item: float(item[1]["y"]))[0]

pairs = [
    (west, east),
    (south, north),
    (west, north),
    (south, east)
]

def heuristic(u, v):
    x1 = float(H.nodes[u]["x"])
    y1 = float(H.nodes[u]["y"])
    x2 = float(H.nodes[v]["x"])
    y2 = float(H.nodes[v]["y"])
    return math.hypot(x2 - x1, y2 - y1)

def route_metrics(graph, path):

    distance = 0
    weighted_risk = 0

    for u, v in zip(path[:-1], path[1:]):
        edge = graph[u][v]
        length = edge["length"]
        probability = edge["probability"]

        distance += length
        weighted_risk += length * probability

    return distance, weighted_risk / distance

for number, (source, target) in enumerate(pairs, start=1):

    print("\nTEST", number, flush=True)

    if source == target:
        print("Skipped: source and destination are identical.")
        continue

    if not nx.has_path(D, source, target):
        print("No directed route available.")
        continue

    distance_path = nx.astar_path(
        D, source, target,
        heuristic=heuristic,
        weight="cost"
    )

    flood_path = nx.astar_path(
        F, source, target,
        heuristic=heuristic,
        weight="cost"
    )

    distance_length, distance_risk = route_metrics(D, distance_path)
    flood_length, flood_risk = route_metrics(F, flood_path)

    print("Shortest route:", round(distance_length / 1000, 3), "km")
    print("Shortest route risk:", format(distance_risk, ".6f"))

    print("Flood-aware route:", round(flood_length / 1000, 3), "km")
    print("Flood-aware route risk:", format(flood_risk, ".6f"))

    print("Distance change:",
          round((flood_length - distance_length) / 1000, 3), "km")

    print("Risk change:",
          format(flood_risk - distance_risk, ".6f"))

    if flood_risk < distance_risk:
        print("Result: Flood-aware route has lower estimated risk.")
    elif flood_risk > distance_risk:
        print("Result: Flood-aware route has higher estimated risk.")
    else:
        print("Result: Both routes have equal estimated risk.")

print("\nMULTIPLE ROUTE TEST COMPLETED")
