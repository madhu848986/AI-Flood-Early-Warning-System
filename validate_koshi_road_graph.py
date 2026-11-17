
import networkx as nx

FILE = "datasets/processed/koshi_junction_road_graph.graphml"

print("Loading improved road graph...", flush=True)

G = nx.read_graphml(FILE, node_type=str)

print("NODES:", G.number_of_nodes())
print("DIRECTED EDGES:", G.number_of_edges())

print("Checking weak connectivity...", flush=True)

weak_components = list(nx.weakly_connected_components(G))

print("WEAK COMPONENTS:", len(weak_components))
print("LARGEST WEAK COMPONENT:", max(len(c) for c in weak_components))

print("Checking strong connectivity...", flush=True)

strong_components = list(nx.strongly_connected_components(G))

print("STRONG COMPONENTS:", len(strong_components))
print("LARGEST STRONG COMPONENT:", max(len(c) for c in strong_components))

print("SELF LOOPS:", nx.number_of_selfloops(G))

lengths = [
    float(data["length_m"])
    for _, _, data in G.edges(data=True)
]

print("INVALID EDGE LENGTHS:", sum(
    value <= 0 for value in lengths
))

print("GRAPH VALIDATION COMPLETED")
