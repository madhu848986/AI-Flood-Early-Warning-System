import geopandas as gpd
import pandas as pd

source = "datasets/processed/koshi_vehicle_roads.gpkg"
output = "datasets/processed/koshi_vehicle_roads_grade.gpkg"

print("Loading roads...")
roads = gpd.read_file(source)

tags = roads["other_tags"].fillna("").astype(str)

roads["layer"] = (
    tags.str.extract(r'"layer"=>"([^"]+)"', expand=False)
    .fillna("0")
)

roads["layer"] = pd.to_numeric(roads["layer"], errors="coerce").fillna(0).astype(int)

roads["bridge"] = tags.str.contains(r'"bridge"=>', regex=True)
roads["tunnel"] = tags.str.contains(r'"tunnel"=>', regex=True)
roads["ford"] = tags.str.contains(r'"ford"=>', regex=True)

print("\nROAD-LEVEL ATTRIBUTE SUMMARY")
print("Total roads:", len(roads))
print("Bridge roads:", roads["bridge"].sum())
print("Tunnel roads:", roads["tunnel"].sum())
print("Ford roads:", roads["ford"].sum())

print("\nLayer counts:")
print(roads["layer"].value_counts().sort_index())

roads.to_file(output, driver="GPKG")

print("\nSaved:", output)
print("ROAD-LEVEL ATTRIBUTES CREATED SUCCESSFULLY")