
import networkx as nx
import pandas as pd
import numpy as np
from pyproj import Transformer
from scipy.spatial import cKDTree

GRAPH_FILE = "datasets/processed/koshi_coordinate_road_graph.graphml"
FLOOD_FILE = "datasets/processed/koshi_all_grid_flood_predictions.csv"
OUTPUT_FILE = "datasets/processed/koshi_flood_risk_road_graph.graphml"

print("Loading flood-grid data...", flush=True)

df = pd.read_csv(FLOOD_FILE)

transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32645",
    always_xy=True
)

grid_x, grid_y = transformer.transform(
    df["longitude"].to_numpy(),
    df["latitude"].to_numpy()
)

grid_coordinates = np.column_stack((grid_x, grid_y))

tree = cKDTree(grid_coordinates)

probabilities = df["flood_probability"].to_numpy()
categories = df["risk_category"].to_numpy()

print("Flood cells loaded:", len(df), flush=True)

print("Loading road graph...", flush=True)

G = nx.read_graphml(
    GRAPH_FILE,
    node_type=str
)

print("Matching road segments...", flush=True)

matched = 0
distances = []

for u, v, key, data in G.edges(
    keys=True,
    data=True
):

    x1 = float(G.nodes[u]["x"])
    y1 = float(G.nodes[u]["y"])

    x2 = float(G.nodes[v]["x"])
    y2 = float(G.nodes[v]["y"])

    midpoint = [
        (x1 + x2) / 2,
        (y1 + y2) / 2
    ]

    distance, index = tree.query(midpoint)

    data["flood_probability"] = float(
        probabilities[index]
    )

    data["risk_category"] = str(
        categories[index]
    )

    data["grid_distance_m"] = float(distance)

    matched += 1
    distances.append(distance)

    if matched % 100000 == 0:
        print("Segments matched:", matched, flush=True)

print("Saving risk-enriched graph...", flush=True)

nx.write_graphml(G, OUTPUT_FILE)

print("RISK MATCHING COMPLETED")
print("DIRECTED EDGES MATCHED:", matched)
print("MEAN GRID DISTANCE:", round(float(np.mean(distances)), 2), "m")
print("MAXIMUM GRID DISTANCE:", round(float(np.max(distances)), 2), "m")
print("OUTPUT:", OUTPUT_FILE)
