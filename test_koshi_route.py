
import networkx as nx

FILE = "datasets/processed/koshi_junction_road_graph.graphml"

print("Loading graph...", flush=True)
G = nx.read_graphml(FILE, node_type=str)

print("Finding largest weak component...", flush=True)
components = list(nx.weakly_connected_components(G))
largest = max(components, key=len)

H = G.subgraph(largest).copy()

nodes = list(H.nodes())

source = nodes[0]
target = nodes[-1]

print("SOURCE:", source)
print("TARGET:", target)
print("Testing shortest-distance route...", flush=True)

try:
    path = nx.shortest_path(
        H,
        source=source,
        target=target,
        weight="length_m"
    )

    distance = nx.shortest_path_length(
        H,
        source=source,
        target=target,
        weight="length_m"
    )

    print("ROUTE FOUND")
    print("PATH NODES:", len(path))
    print("TOTAL DISTANCE:", round(distance, 2), "metres")

except nx.NetworkXNoPath:
    print("NO ROUTE FOUND")

print("ROUTE TEST COMPLETED")
