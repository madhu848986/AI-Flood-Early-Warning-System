
import networkx as nx
import math

FILE = "datasets/processed/koshi_flood_risk_road_graph.graphml"

SOURCE = "J_45643"
TARGET = "J_62200"

LAMBDA = 50.0

print("Loading flood-risk graph...", flush=True)

G = nx.read_graphml(FILE, node_type=str)

def heuristic(node, destination):
    x1 = float(G.nodes[node]["x"])
    y1 = float(G.nodes[node]["y"])
    x2 = float(G.nodes[destination]["x"])
    y2 = float(G.nodes[destination]["y"])

    return math.hypot(x2 - x1, y2 - y1)

def distance_cost(u, v, edges):
    return min(
        float(data["length_m"])
        for data in edges.values()
    )

def flood_cost(u, v, edges):
    return min(
        float(data["length_m"]) *
        (1 + LAMBDA * float(data["flood_probability"]))
        for data in edges.values()
    )

def selected_edge(u, v, cost_function):
    edges = G.get_edge_data(u, v)

    return min(
        edges.values(),
        key=lambda data: cost_function(u, v, {0: data})
    )

def route_metrics(path, cost_function):
    total_distance = 0
    weighted_probability = 0
    total_cost = 0

    for u, v in zip(path[:-1], path[1:]):
        data = selected_edge(u, v, cost_function)

        length = float(data["length_m"])
        probability = float(data["flood_probability"])

        total_distance += length
        weighted_probability += length * probability
        total_cost += length * (1 + LAMBDA * probability)

    average_probability = weighted_probability / total_distance

    return total_distance, average_probability, total_cost

print("Calculating shortest-distance route...", flush=True)

normal_path = nx.astar_path(
    G, SOURCE, TARGET,
    heuristic=heuristic,
    weight=distance_cost
)

normal_distance, normal_risk, normal_cost = route_metrics(
    normal_path, distance_cost
)

print("Calculating flood-aware route...", flush=True)

risk_path = nx.astar_path(
    G, SOURCE, TARGET,
    heuristic=heuristic,
    weight=flood_cost
)

risk_distance, risk_average, risk_total_cost = route_metrics(
    risk_path, flood_cost
)

print("\nROUTE COMPARISON")
print("PENALTY STRENGTH:", LAMBDA)

print("\nSHORTEST-DISTANCE ROUTE")
print("NODES:", len(normal_path))
print("DISTANCE:", round(normal_distance, 2), "m")
print("AVERAGE FLOOD PROBABILITY:", round(normal_risk, 4))

print("\nFLOOD-AWARE ROUTE")
print("NODES:", len(risk_path))
print("DISTANCE:", round(risk_distance, 2), "m")
print("AVERAGE FLOOD PROBABILITY:", round(risk_average, 4))
print("WEIGHTED ROUTE COST:", round(risk_total_cost, 2))

print("\nROUTE TEST COMPLETED")
