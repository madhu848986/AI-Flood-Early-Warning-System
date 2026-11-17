
import networkx as nx

FILE = "datasets/processed/koshi_bilinear_flood_risk_road_graph.graphml"

SOURCE = "E_384619.08_2961652.56"
TARGET = "J_90016"

G = nx.read_graphml(FILE, node_type=str)

for LAMBDA in [0, 5, 10, 20, 50, 100]:

    H = nx.DiGraph()

    for u, v, key, data in G.edges(keys=True, data=True):
        length = float(data["length_m"])
        risk = float(data["flood_probability"])
        cost = length * (1 + LAMBDA * risk)

        if not H.has_edge(u, v) or cost < H[u][v]["cost"]:
            H.add_edge(
                u, v,
                length=length,
                risk=risk,
                cost=cost
            )

    path = nx.shortest_path(
        H, SOURCE, TARGET, weight="cost"
    )

    distance = 0
    weighted_risk = 0

    for u, v in zip(path[:-1], path[1:]):
        edge = H[u][v]
        distance += edge["length"]
        weighted_risk += edge["length"] * edge["risk"]

    average_risk = weighted_risk / distance

    print(
        "Lambda:", LAMBDA,
        "| Distance:", round(distance / 1000, 3), "km",
        "| Estimated risk:", round(average_risk, 5),
        "| Junctions:", len(path)
    )
