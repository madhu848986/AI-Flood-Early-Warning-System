import pandas as pd

file = "datasets/processed/koshi_shelter_recommendations.csv"
data = pd.read_csv(file)

repeated = data[data.duplicated("osm_id", keep=False)]
summary = repeated.sort_values("osm_id")

print("Total shelter records:", len(data))
print("Unique OSM IDs:", data["osm_id"].nunique())
print("Records with repeated OSM IDs:", len(repeated))

print("\nRepeated OSM ID records:")
print(summary[["osm_id", "name", "longitude", "latitude"]].to_string(index=False))