import geopandas as gpd

file = "datasets/processed/koshi_vehicle_roads.gpkg"

print("Loading roads...")

roads = gpd.read_file(file)

tags = roads["other_tags"].fillna("")

checks = {
    "bridge": r'"bridge"=>',
    "tunnel": r'"tunnel"=>',
    "layer": r'"layer"=>',
    "ford": r'"ford"=>'
}

print("\nBRIDGE AND TUNNEL ANALYSIS")

for name, pattern in checks.items():

    count = tags.str.contains(
        pattern,
        regex=True
    ).sum()

    print(name, ":", count)

print("\nSAMPLE BRIDGE RECORDS")

print(
    roads[
        tags.str.contains(r'"bridge"=>', regex=True)
    ][["osm_id", "highway", "other_tags"]]
    .head(10)
    .to_string(index=False)
)

print("\nSAMPLE TUNNEL RECORDS")

print(
    roads[
        tags.str.contains(r'"tunnel"=>', regex=True)
    ][["osm_id", "highway", "other_tags"]]
    .head(10)
    .to_string(index=False)
)