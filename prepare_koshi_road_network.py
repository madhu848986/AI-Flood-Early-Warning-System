import geopandas as gpd
import pandas as pd

input_file = "datasets/raw/osm/koshi/koshi_roads.geojson"

output_file = "datasets/processed/koshi_vehicle_roads.gpkg"

allowed_roads = [
    "motorway", "motorway_link",
    "trunk", "trunk_link",
    "primary", "primary_link",
    "secondary", "secondary_link",
    "tertiary", "tertiary_link",
    "unclassified", "residential",
    "living_street", "service", "road"
]

print("Loading road network...")

roads = gpd.read_file(input_file)

roads = roads[
    roads["highway"].isin(allowed_roads)
].copy()

roads = roads.to_crs("EPSG:32645")

roads["length_m"] = roads.geometry.length

tags = roads["other_tags"].fillna("")

roads["oneway"] = "no"

roads.loc[
    tags.str.contains(r'"oneway"=>"yes"', regex=True),
    "oneway"
] = "yes"

roads.loc[
    tags.str.contains(r'"oneway"=>"-1"', regex=True),
    "oneway"
] = "-1"

roads = roads[
    ["osm_id", "name", "highway",
     "oneway", "length_m", "other_tags", "geometry"]
]
roads.to_file(
    output_file,
    driver="GPKG"
)

print("\nROAD NETWORK PREPARATION COMPLETED")
print("Total selected roads:", len(roads))
print("\nRoad direction counts:")
print(roads["oneway"].value_counts())

print("\nRoad category counts:")
print(roads["highway"].value_counts())

print("\nSaved:", output_file)