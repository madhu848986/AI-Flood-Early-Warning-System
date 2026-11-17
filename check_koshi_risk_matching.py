
import networkx as nx
import numpy as np

FILE = "datasets/processed/koshi_flood_risk_road_graph.graphml"

print("Loading graph...", flush=True)
G = nx.read_graphml(FILE, node_type=str)

distances = np.array([
    float(data["grid_distance_m"])
    for _, _, data in G.edges(data=True)
])

print("TOTAL EDGES:", len(distances))
print("MINIMUM DISTANCE:", round(distances.min(), 2), "m")
print("MEDIAN DISTANCE:", round(np.median(distances), 2), "m")
print("MEAN DISTANCE:", round(distances.mean(), 2), "m")
print("90TH PERCENTILE:", round(np.percentile(distances, 90), 2), "m")
print("95TH PERCENTILE:", round(np.percentile(distances, 95), 2), "m")

print("WITHIN 1 KM:", np.sum(distances <= 1000))
print("WITHIN 2 KM:", np.sum(distances <= 2000))
print("WITHIN 5 KM:", np.sum(distances <= 5000))

print("DISTANCE QUALITY CHECK COMPLETED")
