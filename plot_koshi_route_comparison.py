
import networkx as nx
import matplotlib.pyplot as plt
import math
from matplotlib.lines import Line2D

FILE = "datasets/processed/koshi_bilinear_flood_risk_road_graph.graphml"

SOURCE = "J_45643"
TARGET = "J_62200"
LAMBDA = 10.0

print("Loading flood-risk road graph...", flush=True)

G = nx.read_graphml(FILE, node_type=str)

print("Finding largest strongly connected component...", flush=True)

components = list(nx.strongly_connected_components(G))
largest = max(components, key=len)
H = G.subgraph(largest).copy()

if SOURCE not in H or TARGET not in H:
    raise ValueError("Source or destination is not in the largest component.")

print("Preparing route graphs...", flush=True)

D = nx.DiGraph()
F = nx.DiGraph()

for u, v, key, data in H.edges(keys=True, data=True):

    length = float(data["length_m"])
    probability = float(data["flood_probability"])

    flood_cost = length * (1 + LAMBDA * probability)

    if not D.has_edge(u, v) or length < D[u][v]["length"]:
        D.add_edge(
            u, v,
            length=length,
            probability=probability,
            cost=length
        )

    if not F.has_edge(u, v) or flood_cost < F[u][v]["cost"]:
        F.add_edge(
            u, v,
            length=length,
            probability=probability,
            cost=flood_cost
        )

def heuristic(u, v):

    x1 = float(H.nodes[u]["x"])
    y1 = float(H.nodes[u]["y"])
    x2 = float(H.nodes[v]["x"])
    y2 = float(H.nodes[v]["y"])

    return math.hypot(x2 - x1, y2 - y1)

print("Calculating shortest-distance route...", flush=True)

shortest_path = nx.astar_path(
    D, SOURCE, TARGET,
    heuristic=heuristic,
    weight="cost"
)

print("Calculating flood-aware route...", flush=True)

flood_path = nx.astar_path(
    F, SOURCE, TARGET,
    heuristic=heuristic,
    weight="cost"
)

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

shortest_distance, shortest_risk = get_metrics(D, shortest_path)
flood_distance, flood_risk = get_metrics(F, flood_path)

print("\nROUTE COMPARISON")
print("Shortest route distance:", round(shortest_distance / 1000, 3), "km")
print("Shortest route risk:", round(shortest_risk, 6))
print("Flood-aware route distance:", round(flood_distance / 1000, 3), "km")
print("Flood-aware route risk:", round(flood_risk, 6))

print("\nPreparing route visualization...", flush=True)

fig, ax = plt.subplots(figsize=(12, 10))

def draw_route(path, color, width):

    x_values = []
    y_values = []

    for node in path:

        x_values.append(float(H.nodes[node]["x"]))
        y_values.append(float(H.nodes[node]["y"]))

    ax.plot(
        x_values,
        y_values,
        color=color,
        linewidth=width,
        solid_capstyle="round"
    )

draw_route(shortest_path, "royalblue", 3)
draw_route(flood_path, "darkorange", 2.5)

source_x = float(H.nodes[SOURCE]["x"])
source_y = float(H.nodes[SOURCE]["y"])

target_x = float(H.nodes[TARGET]["x"])
target_y = float(H.nodes[TARGET]["y"])

ax.scatter(source_x, source_y, color="green", s=100, zorder=5)
ax.scatter(target_x, target_y, color="red", s=100, zorder=5)

ax.annotate("Source", (source_x, source_y), xytext=(6, 8),
            textcoords="offset points")

ax.annotate("Destination", (target_x, target_y), xytext=(6, 8),
            textcoords="offset points")

legend_items = [
    Line2D([0], [0], color="royalblue", linewidth=3,
           label="Shortest-distance route"),
    Line2D([0], [0], color="darkorange", linewidth=2.5,
           label="Flood-aware route (Lambda 10)"),
    Line2D([0], [0], marker="o", color="green",
           linestyle="None", markersize=8, label="Source"),
    Line2D([0], [0], marker="o", color="red",
           linestyle="None", markersize=8, label="Destination")
]

ax.legend(handles=legend_items, loc="best")

ax.set_title("Koshi Basin: Shortest vs Flood-Aware Route")
ax.set_xlabel("Easting (metres, EPSG:32645)")
ax.set_ylabel("Northing (metres, EPSG:32645)")
ax.set_aspect("equal", adjustable="datalim")
ax.grid(True, alpha=0.25)

plt.tight_layout()

OUTPUT = "datasets/processed/eda/koshi_route_comparison.png"

plt.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.close()

print("\nRoute map saved:", OUTPUT)
print("ROUTE VISUALIZATION COMPLETED")
