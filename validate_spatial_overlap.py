import pandas as pd

rainfall_path = (
    "datasets/processed/koshi_rainfall_october_13_14_2021.csv"
)

flood_path = (
    "datasets/processed/koshi_modis_flood_cell_summary.csv"
)

rainfall = pd.read_csv(rainfall_path)
flood = pd.read_csv(flood_path)

# Normalize coordinates before matching
for df in (rainfall, flood):
    df["latitude"] = df["latitude"].round(6)
    df["longitude"] = df["longitude"].round(6)

rain_cells = rainfall[
    ["latitude", "longitude"]
].drop_duplicates()

flood_cells = flood[
    ["latitude", "longitude"]
].drop_duplicates()

matched = rain_cells.merge(
    flood_cells,
    on=["latitude", "longitude"],
    how="inner",
)

print("SPATIAL OVERLAP VALIDATION")
print("=" * 45)
print("Unique rainfall cells:", len(rain_cells))
print("Flood cells with valid observations:", len(flood_cells))
print("Matching cells:", len(matched))
print("Rainfall cells without flood observations:",
      len(rain_cells) - len(matched))

print("\nMatched coordinate ranges:")
print("Latitude:", matched["latitude"].min(),
      "to", matched["latitude"].max())
print("Longitude:", matched["longitude"].min(),
      "to", matched["longitude"].max())

print("\nMatched cells by latitude:")
print(matched.groupby(
    matched["latitude"].round(1)
).size().to_string())

print("\nMatched cells by longitude:")
print(matched.groupby(
    matched["longitude"].round(1)
).size().to_string())