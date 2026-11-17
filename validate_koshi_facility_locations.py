
import geopandas as gpd
import pandas as pd

file = "datasets/raw/osm/koshi/koshi_potential_facilities.geojson"

gdf = gpd.read_file(file)

print("TOTAL FEATURES:", len(gdf))
print("CRS:", gdf.crs)

print("\nGEOMETRY TYPES:")
print(gdf.geometry.geom_type.value_counts())

print("\nGEOMETRY QUALITY:")
print("Empty geometries:", gdf.geometry.is_empty.sum())
print("Invalid geometries:", (~gdf.geometry.is_valid).sum())
print("Missing geometries:", gdf.geometry.isna().sum())

print("\nSTUDY AREA CHECK:")
print("Longitude range: 85.05 to 88.45")
print("Latitude range: 26.05 to 28.45")

if gdf.crs is not None:
    gdf = gdf.to_crs("EPSG:4326")

    valid = gdf.geometry.notna() & ~gdf.geometry.is_empty
    inside = (
        valid
        & gdf.geometry.x.between(85.05, 88.45)
        & gdf.geometry.y.between(26.05, 28.45)
    ) if gdf.geometry.geom_type.eq("Point").all() else None

    if inside is not None:
        print("Points inside study bounds:", inside.sum())
        print("Points outside study bounds:", (~inside & valid).sum())
    else:
        print("Dataset contains non-point geometries.")
        print("Bounds:", gdf.total_bounds)

print("\nFEATURE COLUMNS:")
print(gdf.columns.tolist())
