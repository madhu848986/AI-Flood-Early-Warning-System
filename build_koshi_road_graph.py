import geopandas as gpd
import networkx as nx

input_file = "datasets/processed/koshi_vehicle_roads.gpkg"
output_file = "datasets/processed/koshi_road_graph.graphml"

print("Loading prepared roads...")

roads = gpd.read_file(input_file)

G = nx.MultiDiGraph()

for _, road in roads.iterrows():

    coordinates = list(road.geometry.coords)

    start = (
        f"{coordinates[0][0]:.6f},"
        f"{coordinates[0][1]:.6f}"
    )

    end = (
        f"{coordinates[-1][0]:.6f},"
        f"{coordinates[-1][1]:.6f}"
    )

    if start == end:
        continue

    attributes = {
        "length_m": float(road["length_m"]),
        "highway": str(road["highway"]),
        "osm_id": str(road["osm_id"])
    }

    direction = road["oneway"]

    if direction == "yes":
        G.add_edge(start, end, **attributes)

    elif direction == "-1":
        G.add_edge(end, start, **attributes)

    else:
        G.add_edge(start, end, **attributes)
        G.add_edge(end, start, **attributes)

print("\nUPDATED ROAD GRAPH")

print("Total nodes:", G.number_of_nodes())
print("Total directed edges:", G.number_of_edges())

components = list(nx.weakly_connected_components(G))

print("Weakly connected components:", len(components))

if components:
    largest = max(components, key=len)

    print("Largest component nodes:", len(largest))

    print(
        "Largest component percentage:",
        round(len(largest) / G.number_of_nodes() * 100, 2)
    )

nx.write_graphml(G, output_file)

print("\nSaved:", output_file)