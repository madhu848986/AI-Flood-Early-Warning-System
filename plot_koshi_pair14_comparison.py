
import networkx as nx
import matplotlib.pyplot as plt

GRAPH_FILE = "datasets/processed/koshi_bilinear_flood_risk_road_graph.graphml"
OUTPUT_FILE = "datasets/processed/eda/koshi_route_comparison_pair14.png"

SOURCE = "E_384619.08_2961652.56"
TARGET = "J_90016"
LAMBDA = 10

G = nx.read_graphml(GRAPH_FILE)

largest_scc = max(nx.strongly_connected_components(G), key=len)
G = G.subgraph(largest_scc).copy()

if SOURCE not in G or TARGET not in G:
    raise ValueError("Source or destination is not in the largest strongly connected component.")

distance_graph = nx.DiGraph()
flood_graph = nx.DiGraph()

for u, v, key, data in G.edges(keys=True, data=True):
    length = float(data["length_m"])
    probability = float(data["flood_probability"])

    distance_cost = length
    flood_cost = length * (1 + LAMBDA * probability)

    if not distance_graph.has_edge(u, v) or distance_cost < distance_graph[u][v]["cost"]:
        distance_graph.add_edge(u, v, cost=distance_cost)

    if not flood_graph.has_edge(u, v) or flood_cost < flood_graph[u][v]["cost"]:
        flood_graph.add_edge(
            u, v,
            cost=flood_cost,
            length=length,
            probability=probability
        )

shortest_route = nx.astar_path(
    distance_graph, SOURCE, TARGET, weight="cost"
)

flood_route = nx.astar_path(
    flood_graph, SOURCE, TARGET, weight="cost"
)

def calculate_metrics(route, graph):
    distance = 0
    risk_sum = 0

    for u, v in zip(route[:-1], route[1:]):
        edge = graph[u][v]
        distance += edge["length"]
        risk_sum += edge["length"] * edge["probability"]

    return distance, risk_sum / distance

shortest_distance, shortest_risk = calculate_metrics(
    shortest_route, flood_graph
)

flood_distance, flood_risk = calculate_metrics(
    flood_route, flood_graph
)

print("\nPAIR 14 ROUTE COMPARISON")
print("Shortest route distance:", round(shortest_distance / 1000, 3), "km")
print("Shortest route risk:", round(shortest_risk, 6))
print("Flood-aware route distance:", round(flood_distance / 1000, 3), "km")
print("Flood-aware route risk:", round(flood_risk, 6))

risk_reduction = shortest_risk - flood_risk
risk_reduction_percent = (risk_reduction / shortest_risk) * 100
extra_distance = flood_distance - shortest_distance

print("Estimated risk reduction:", round(risk_reduction_percent, 2), "%")
print("Additional distance:", round(extra_distance / 1000, 3), "km")

def get_coordinates(route):
    return (
        [float(G.nodes[node]["x"]) for node in route],
        [float(G.nodes[node]["y"]) for node in route]
    )

sx, sy = get_coordinates(shortest_route)
fx, fy = get_coordinates(flood_route)

source_x = float(G.nodes[SOURCE]["x"])
source_y = float(G.nodes[SOURCE]["y"])
target_x = float(G.nodes[TARGET]["x"])
target_y = float(G.nodes[TARGET]["y"])

plt.figure(figsize=(13, 9))

plt.plot(sx, sy, color="blue", linewidth=2,
         label="Shortest-distance route")

plt.plot(fx, fy, color="orange", linewidth=2,
         label="Flood-aware route (Lambda 10)")

plt.scatter(source_x, source_y, color="green", s=90, label="Source")
plt.scatter(target_x, target_y, color="red", s=90, label="Destination")

plt.title("Koshi Basin: Pair 14 Shortest vs Flood-Aware Route")
plt.xlabel("Easting (metres, EPSG:32645)")
plt.ylabel("Northing (metres, EPSG:32645)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(OUTPUT_FILE, dpi=300)
plt.show()

print("\nRoute map saved:", OUTPUT_FILE)
print("PAIR 14 ROUTE VISUALIZATION COMPLETED")
