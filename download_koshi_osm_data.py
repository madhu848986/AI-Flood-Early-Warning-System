
from pathlib import Path
import osmnx as ox
import geopandas as gpd

RAW_DIR = Path("datasets/raw/osm")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Bounding box: left, bottom, right, top
bbox = (85.05, 26.05, 88.45, 28.45)

ox.settings.timeout = 300
ox.settings.use_cache = True
ox.settings.log_console = True

print("Downloading Koshi Basin road network...")

G = ox.graph.graph_from_bbox(
    bbox,
    network_type="drive",
    simplify=True,
    retain_all=True
)

edges = ox.convert.graph_to_gdfs(
    G,
    nodes=False,
    edges=True
)

edges.to_file(
    RAW_DIR / "koshi_roads.geojson",
    driver="GeoJSON"
)

ox.io.save_graphml(
    G,
    filepath=RAW_DIR / "koshi_road_network.graphml"
)

print("Road edges:", len(edges))

print("\nDownloading potential public shelter facilities...")

tags = {
    "amenity": [
        "shelter",
        "hospital",
        "school",
        "community_centre"
    ],
    "social_facility": True,
    "emergency": True
}

facilities = ox.features.features_from_bbox(
    bbox,
    tags
)

if not facilities.empty:
    facilities = facilities.reset_index()
    facilities.to_file(
        RAW_DIR / "koshi_potential_shelters.geojson",
        driver="GeoJSON"
    )

    facilities.drop(columns="geometry").to_csv(
        RAW_DIR / "koshi_potential_shelters.csv",
        index=False
    )

print("Potential facilities:", len(facilities))

print("\nOSM DOWNLOAD COMPLETED")
print("Output folder:", RAW_DIR)
