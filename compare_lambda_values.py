
import networkx as nx
import math

FILE = "datasets/processed/koshi_bilinear_flood_risk_road_graph.graphml"

LAMBDAS = [5.0, 10.0, 20.0]

print("Loading road graph...", flush=True)

G = nx.read_graphml(FILE, node_type=str)

components = list(nx.weakly_connected_components(G))
largest = max(components, key=len)
H = G.subgraph(largest).copy()

print("Largest component:", len(H.nodes), "nodes", flush=True)

D = nx.DiGraph()

for u, v, key, data in H.edges(keys=True, data=True):

    length = float(data["length_m"])
    probability = float(data["flood_probability"])

    if not D.has_edge(u, v) or length < D[u][v]["length"]:
        D.add_edge(
            u, v,
            length=length,
            probability=probability,
            cost=length
        )

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

def get_metrics(graph, path):

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

    print("\n========== TEST", number, "==========", flush=True)

    if not nx.has_path(D, source, target):
        print("No directed route available.")
        continue

    shortest_path = nx.astar_path(
        D, source, target,
        heuristic=heuristic,
        weight="cost"
    )

    shortest_distance, shortest_risk = get_metrics(D, shortest_path)

    print("Shortest distance:", round(shortest_distance / 1000, 3), "km")
    print("Shortest route risk:", format(shortest_risk, ".6f"))

    for lam in LAMBDAS:

        F = nx.DiGraph()

        for u, v, data in D.edges(data=True):

            length = data["length"]
            probability = data["probability"]

            cost = length * (1 + lam * probability)

            F.add_edge(
                u, v,
                length=length,
                probability=probability,
                cost=cost
            )

        flood_path = nx.astar_path(
            F, source, target,
            heuristic=heuristic,
            weight="cost"
        )

        flood_distance, flood_risk = get_metrics(F, flood_path)

        distance_change = flood_distance - shortest_distance

        risk_reduction = shortest_risk - flood_risk

        print("\nLambda:", lam)
        print("Flood-aware distance:", round(flood_distance / 1000, 3), "km")
        print("Extra distance:", round(distance_change / 1000, 3), "km")
        print("Flood-aware risk:", format(flood_risk, ".6f"))
        print("Risk reduction:", format(risk_reduction, ".6f"))

print("\nLAMBDA COMPARISON COMPLETED")
