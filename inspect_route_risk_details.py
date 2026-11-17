import networkx as nx

FILE = "datasets/processed/koshi_flood_risk_road_graph.graphml"

G = nx.read_graphml(FILE, node_type=str)

H = nx.DiGraph()

for u, v, key, data in G.edges(keys=True, data=True):
    length = float(data["length_m"])
    probability = float(data["flood_probability"])
    cost = length * (1 + 20 * probability)

    if not H.has_edge(u, v) or cost < H[u][v]["cost"]:
        H.add_edge(
            u, v,
            length=length,
            probability=probability,
            cost=cost
        )

routes = nx.shortest_simple_paths(
    H, "J_45643", "J_62200", weight="cost"
)

for number, path in enumerate(routes, start=1):
    total_distance = 0
    weighted_risk = 0
    risk_values = []

    for u, v in zip(path[:-1], path[1:]):
        edge = H[u][v]

        length = edge["length"]
        risk = edge["probability"]

        total_distance += length
        weighted_risk += length * risk
        risk_values.append(risk)

    average_risk = weighted_risk / total_distance

    print("\nROUTE", number)
    print("EXACT AVERAGE RISK:", average_risk)
    print("MINIMUM RISK:", min(risk_values))
    print("MAXIMUM RISK:", max(risk_values))
    print("UNIQUE RISK VALUES:", len(set(risk_values)))

    if number == 5:
        break