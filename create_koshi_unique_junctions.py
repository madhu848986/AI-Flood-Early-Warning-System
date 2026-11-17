import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

input_file = "datasets/processed/koshi_road_intersection_points.gpkg"
output_file = "datasets/processed/koshi_unique_road_junctions.gpkg"

data = gpd.read_file(input_file)

data = data[
    data["decision"].isin([
        "at_grade_candidate",
        "endpoint_candidate"
    ])
].copy()

data["x"] = data.geometry.x.round(2)
data["y"] = data.geometry.y.round(2)

records = []

for (x, y), group in data.groupby(["x", "y"]):

    road_ids = sorted(
        set(group["road_i"]).union(set(group["road_j"]))
    )

    decisions = sorted(group["decision"].unique())

    records.append({
        "junction_id": len(records),
        "road_count": len(road_ids),
        "road_indices": ",".join(map(str, road_ids)),
        "decisions": ",".join(decisions),
        "geometry": Point(x, y)
    })

junctions = gpd.GeoDataFrame(
    records,
    geometry="geometry",
    crs=data.crs
)

junctions.to_file(output_file, driver="GPKG")

print("Unique junction dataset created successfully")
print("Total junctions:", len(junctions))
print("\nRoad count distribution:")
print(junctions["road_count"].value_counts().sort_index())

print("\nOutput:", output_file)