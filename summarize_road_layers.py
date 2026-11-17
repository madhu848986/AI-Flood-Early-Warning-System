import geopandas as gpd
import re
from collections import Counter

file = "datasets/processed/koshi_vehicle_roads.gpkg"

print("Loading roads...")
roads = gpd.read_file(file)

layer_counts = Counter()
bridge_layers = Counter()
tunnel_layers = Counter()

for _, row in roads.iterrows():
    value = row["other_tags"]
    tags = value if isinstance(value, str) else ""

    layer_match = re.search(r'"layer"=>"([^"]+)"', tags)
    bridge_match = re.search(r'"bridge"=>"([^"]+)"', tags)
    tunnel_match = re.search(r'"tunnel"=>"([^"]+)"', tags)

    layer = layer_match.group(1) if layer_match else "0"

    layer_counts[layer] += 1

    if bridge_match:
        bridge_layers[layer] += 1

    if tunnel_match:
        tunnel_layers[layer] += 1

print("\nROAD LAYER DISTRIBUTION")
for layer, count in sorted(layer_counts.items()):
    print(f"Layer {layer}: {count}")

print("\nBRIDGE LAYER DISTRIBUTION")
for layer, count in sorted(bridge_layers.items()):
    print(f"Layer {layer}: {count}")

print("\nTUNNEL LAYER DISTRIBUTION")
for layer, count in sorted(tunnel_layers.items()):
    print(f"Layer {layer}: {count}")