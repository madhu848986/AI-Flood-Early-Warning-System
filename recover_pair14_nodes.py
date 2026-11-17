
import random
import networkx as nx
import math

GRAPH_FILE = "datasets/processed/koshi_bilinear_flood_risk_road_graph.graphml"

G = nx.read_graphml(GRAPH_FILE)

largest_scc = max(nx.strongly_connected_components(G), key=len)
H = G.subgraph(largest_scc)

nodes = list(H.nodes())
random.seed(42)

pairs = []

while len(pairs) < 20:
    source = random.choice(nodes)
    target = random.choice(nodes)

    if source == target:
        continue

    x1 = float(H.nodes[source]["x"])
    y1 = float(H.nodes[source]["y"])
    x2 = float(H.nodes[target]["x"])
    y2 = float(H.nodes[target]["y"])

    straight_distance = math.hypot(x2 - x1, y2 - y1)

    if straight_distance < 50000:
        continue

    pairs.append((source, target))

print("\nPAIR 14 SOURCE AND DESTINATION")
print("Source:", pairs[13][0])
print("Destination:", pairs[13][1])
