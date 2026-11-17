
import networkx as nx
import math
import random

FILE = "datasets/processed/koshi_bilinear_flood_risk_road_graph.graphml"

LAMBDAS = [5.0, 10.0]
NUMBER_OF_PAIRS = 20
MIN_SEPARATION_KM = 50

random.seed(42)

print("Loading road graph...", flush=True)

G = nx.read_graphml(FILE, node_type=str)

print("Finding largest strongly connected component...", flush=True)

components = list(nx.strongly_connected_components(G))
largest = max(components, key=len)
H = G.subgraph(largest).copy()

print("Strongly connected nodes:", len(H.nodes), flush=True)

print("Preparing distance graph...", flush=True)

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

print("Selecting 20 geographically separated pairs...", flush=True)

nodes = list(H.nodes)
pairs = []
attempts = 0

while len(pairs) < NUMBER_OF_PAIRS and attempts < 100000:

    attempts += 1

    source = random.choice(nodes)
    target = random.choice(nodes)

    if source == target:
        continue

    x1 = float(H.nodes[source]["x"])
    y1 = float(H.nodes[source]["y"])
    x2 = float(H.nodes[target]["x"])
    y2 = float(H.nodes[target]["y"])

    separation = math.hypot(x2 - x1, y2 - y1)

    if separation < MIN_SEPARATION_KM * 1000:
        continue

    pairs.append((source, target))

print("Selected pairs:", len(pairs), flush=True)

results = []

for number, (source, target) in enumerate(pairs, start=1):

    print("\n========== PAIR", number, "==========", flush=True)

    shortest_path = nx.astar_path(
        D, source, target,
        heuristic=heuristic,
        weight="cost"
    )

    shortest_distance, shortest_risk = get_metrics(
        D, shortest_path
    )

    print("Shortest distance:", round(shortest_distance / 1000, 3), "km")
    print("Shortest risk:", format(shortest_risk, ".6f"))

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

        flood_distance, flood_risk = get_metrics(
            F, flood_path
        )

        extra_distance = flood_distance - shortest_distance
        risk_reduction = shortest_risk - flood_risk

        distance_percent = (
            extra_distance / shortest_distance
        ) * 100

        risk_percent = (
            risk_reduction / shortest_risk
        ) * 100 if shortest_risk > 0 else 0

        improved = risk_reduction > 0.0000001

        results.append({
            "pair": number,
            "lambda": lam,
            "shortest_km": shortest_distance / 1000,
            "flood_km": flood_distance / 1000,
            "extra_km": extra_distance / 1000,
            "distance_percent": distance_percent,
            "shortest_risk": shortest_risk,
            "flood_risk": flood_risk,
            "risk_reduction": risk_reduction,
            "risk_percent": risk_percent,
            "improved": improved
        })

        print(
            "Lambda:", lam,
            "| Extra km:", round(extra_distance / 1000, 3),
            "| Extra distance %:", round(distance_percent, 2),
            "| Risk reduction:", format(risk_reduction, ".6f"),
            "| Risk reduction %:", round(risk_percent, 2),
            "| Improved:", improved,
            flush=True
        )

print("\n========== FINAL SUMMARY ==========")

for lam in LAMBDAS:

    selected = [
        item for item in results
        if item["lambda"] == lam
    ]

    improved_count = sum(
        1 for item in selected if item["improved"]
    )

    average_extra = sum(
        item["extra_km"] for item in selected
    ) / len(selected)

    average_distance_percent = sum(
        item["distance_percent"] for item in selected
    ) / len(selected)

    average_risk_reduction = sum(
        item["risk_reduction"] for item in selected
    ) / len(selected)

    average_risk_percent = sum(
        item["risk_percent"] for item in selected
    ) / len(selected)

    print("\nLAMBDA:", lam)
    print("Routes with lower estimated risk:", improved_count, "/", len(selected))
    print("Average extra distance:", round(average_extra, 3), "km")
    print("Average extra distance percentage:", round(average_distance_percent, 2), "%")
    print("Average risk reduction:", format(average_risk_reduction, ".6f"))
    print("Average risk reduction percentage:", round(average_risk_percent, 2), "%")

import csv

with open(
    "datasets/processed/20_pair_lambda_evaluation.csv",
    "w",
    newline=""
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=results[0].keys()
    )

    writer.writeheader()
    writer.writerows(results)

print("\nResults saved to datasets/processed/20_pair_lambda_evaluation.csv")
print("20-PAIR ROUTING EVALUATION COMPLETED")
