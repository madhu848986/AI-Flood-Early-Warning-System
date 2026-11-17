
import networkx as nx
import pandas as pd
import numpy as np

from pyproj import Transformer
from scipy.interpolate import RegularGridInterpolator

GRID_FILE = "datasets/processed/koshi_all_grid_flood_predictions.csv"

INPUT_GRAPH = "datasets/processed/koshi_flood_risk_road_graph.graphml"

OUTPUT_GRAPH = "datasets/processed/koshi_bilinear_flood_risk_road_graph.graphml"

print("Loading flood prediction grid...", flush=True)

df = pd.read_csv(GRID_FILE)

grid = df.pivot(
    index="latitude",
    columns="longitude",
    values="flood_probability"
)

grid = grid.sort_index().sort_index(axis=1)

latitudes = grid.index.to_numpy()
longitudes = grid.columns.to_numpy()
values = grid.to_numpy()

if np.isnan(values).any():
    raise ValueError("Prediction grid contains missing cells.")

print("GRID SHAPE:", values.shape, flush=True)

interpolator = RegularGridInterpolator(
    (latitudes, longitudes),
    values,
    bounds_error=False,
    fill_value=np.nan
)

transformer = Transformer.from_crs(
    "EPSG:32645",
    "EPSG:4326",
    always_xy=True
)

print("Loading original road graph...", flush=True)

G = nx.read_graphml(INPUT_GRAPH, node_type=str)

print("TOTAL NODES:", G.number_of_nodes(), flush=True)
print("TOTAL EDGES:", G.number_of_edges(), flush=True)

edges = list(G.edges(keys=True, data=True))

mid_x = []
mid_y = []

for u, v, key, data in edges:
    x1 = float(G.nodes[u]["x"])
    y1 = float(G.nodes[u]["y"])

    x2 = float(G.nodes[v]["x"])
    y2 = float(G.nodes[v]["y"])

    mid_x.append((x1 + x2) / 2)
    mid_y.append((y1 + y2) / 2)

print("Converting road midpoints to geographic coordinates...", flush=True)

mid_lon, mid_lat = transformer.transform(
    np.array(mid_x),
    np.array(mid_y)
)

points = np.column_stack((mid_lat, mid_lon))

print("Calculating interpolated flood probabilities...", flush=True)

interpolated = interpolator(points)

outside_count = int(np.isnan(interpolated).sum())

updated_count = 0

for i, (u, v, key, data) in enumerate(edges):

    old_probability = float(data["flood_probability"])

    if np.isnan(interpolated[i]):
        probability = old_probability
    else:
        probability = float(interpolated[i])
        updated_count += 1

    data["flood_probability_nearest"] = old_probability
    data["flood_probability"] = probability

    if probability >= 0.4:
        data["risk_category"] = "High Risk"
    else:
        data["risk_category"] = "Lower Risk"

print("\nINTERPOLATION SUMMARY")
print("TOTAL ROAD EDGES:", len(edges))
print("INTERPOLATED EDGES:", updated_count)
print("OUTSIDE GRID / FALLBACK EDGES:", outside_count)

probabilities = np.array([
    float(data["flood_probability"])
    for u, v, key, data in edges
])

print("MINIMUM PROBABILITY:", probabilities.min())
print("MAXIMUM PROBABILITY:", probabilities.max())
print("MEAN PROBABILITY:", probabilities.mean())
print("UNIQUE PROBABILITIES:", len(np.unique(probabilities)))

print("\nSaving new road graph...", flush=True)

nx.write_graphml(G, OUTPUT_GRAPH)

print("OUTPUT:", OUTPUT_GRAPH)
print("BILINEAR ROAD-RISK ANNOTATION COMPLETED")
