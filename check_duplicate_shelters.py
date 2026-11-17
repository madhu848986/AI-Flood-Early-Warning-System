
import pandas as pd
import geopandas as gpd
from scipy.spatial import cKDTree

input_file = "datasets/processed/koshi_shelter_recommendations.csv"
output_file = "datasets/processed/koshi_possible_duplicate_shelters.csv"

print("Loading shelter recommendations...", flush=True)

data = pd.read_csv(input_file)

geometry = gpd.points_from_xy(
    data["longitude"],
    data["latitude"]
)

gdf = gpd.GeoDataFrame(
    data,
    geometry=geometry,
    crs="EPSG:4326"
).to_crs("EPSG:32645")

coordinates = [
    (point.x, point.y) for point in gdf.geometry
]

tree = cKDTree(coordinates)

pairs = tree.query_pairs(r=30)

records = []

for i, j in sorted(pairs):
    distance = gdf.geometry.iloc[i].distance(
        gdf.geometry.iloc[j]
    )

    records.append({
        "osm_id_1": gdf.iloc[i]["osm_id"],
        "osm_id_2": gdf.iloc[j]["osm_id"],
        "name_1": gdf.iloc[i]["name"],
        "name_2": gdf.iloc[j]["name"],
        "distance_m": round(distance, 2),
        "probability_1": gdf.iloc[i]["flood_probability"],
        "probability_2": gdf.iloc[j]["flood_probability"]
    })

result = pd.DataFrame(records)

result.to_csv(output_file, index=False)

print("\nDUPLICATE SHELTER CHECK COMPLETED")
print("Total shelters:", len(data))
print("Possible nearby duplicate pairs:", len(result))

if len(result):
    print("\nPossible duplicates:")
    print(result.to_string(index=False))
else:
    print("No pairs found within 30 metres.")

print("\nSaved:", output_file)
