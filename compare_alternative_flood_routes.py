
import networkx as nx

FILE = "datasets/processed/koshi_bilinear_flood_risk_road_graph.graphml"

SOURCE = "J_45643"
TARGET = "J_62200"

LAMBDA = 20.0
MAX_ROUTES = 5

print("Loading bilinear flood-risk graph...", flush=True)

G = nx.read_graphml(FILE, node_type=str)

print("Building alternative-route graph...", flush=True)

H = nx.DiGraph()

for u, v, key, data in G.edges(keys=True, data=True):

    length = float(data["length_m"])
    probability = float(data["flood_probability"])

    cost = length * (1 + LAMBDA * probability)

    if not H.has_edge(u, v):
        H.add_edge(
            u, v,
            length=length,
            probability=probability,
            cost=cost
        )

    elif cost < H[u][v]["cost"]:
        H[u][v]["length"] = length
        H[u][v]["probability"] = probability
        H[u][v]["cost"] = cost

print("Searching for alternative routes...", flush=True)

routes = nx.shortest_simple_paths(
    H,
    SOURCE,
    TARGET,
    weight="cost"
)

for number, path in enumerate(routes, start=1):

    total_distance = 0
    weighted_probability = 0
    total_cost = 0
    risk_values = []

    for u, v in zip(path[:-1], path[1:]):

        edge = H[u][v]

        length = edge["length"]
        probability = edge["probability"]

        total_distance += length
        weighted_probability += length * probability
        total_cost += edge["cost"]

        risk_values.append(probability)

    average_probability = weighted_probability / total_distance

    print("\nROUTE", number)
    print("NODES:", len(path))
    print("DISTANCE:", round(total_distance / 1000, 4), "km")

    print(
        "EXACT AVERAGE RISK:",
        format(average_probability, ".10f")
    )

    print(
        "MINIMUM RISK:",
        format(min(risk_values), ".10f")
    )

    print(
        "MAXIMUM RISK:",
        format(max(risk_values), ".10f")
    )

    print("UNIQUE RISK VALUES:", len(set(risk_values)))

    print("FLOOD-AWARE COST:", round(total_cost, 2))

    if number >= MAX_ROUTES:
        break

print("\nALTERNATIVE ROUTE TEST COMPLETED")
