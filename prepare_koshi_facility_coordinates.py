
import geopandas as gpd
import pandas as pd
from shapely import make_valid

input_file = "datasets/raw/osm/koshi/koshi_potential_facilities.geojson"
output_file = "datasets/processed/koshi_facilities_with_coordinates.csv"

gdf = gpd.read_file(input_file)

# Repair invalid geometries
invalid = ~gdf.geometry.is_valid
gdf.loc[invalid, "geometry"] = gdf.loc[invalid, "geometry"].apply(make_valid)

# Convert every feature into a representative point
gdf["representative_point"] = gdf.geometry.representative_point()

gdf["longitude"] = gdf["representative_point"].x
gdf["latitude"] = gdf["representative_point"].y

# Check study-area boundaries
gdf["inside_study_area"] = (
    gdf["longitude"].between(85.05, 88.45)
    & gdf["latitude"].between(26.05, 28.45)
)

# Extract amenity category
tags = gdf["other_tags"].fillna("")
gdf["amenity_type"] = tags.str.extract(
    r'"amenity"=>"([^"]+)"',
    expand=False
)

# Keep only relevant columns
result = pd.DataFrame({
    "osm_id": gdf["osm_id"],
    "name": gdf["name"],
    "amenity_type": gdf["amenity_type"],
    "source_layer": gdf["source_layer"],
    "longitude": gdf["longitude"],
    "latitude": gdf["latitude"],
    "inside_study_area": gdf["inside_study_area"]
})

result.to_csv(output_file, index=False)

print("FACILITY COORDINATE DATASET CREATED")
print("Total features:", len(result))
print("Inside study area:", result["inside_study_area"].sum())
print("Outside study area:", (~result["inside_study_area"]).sum())

print("\nFACILITY TYPES INSIDE STUDY AREA:")
print(
    result[result["inside_study_area"]]["amenity_type"]
    .value_counts(dropna=False)
)

print("\nInvalid geometries remaining:", (~gdf.geometry.is_valid).sum())
print("Missing coordinates:", result[["longitude", "latitude"]].isna().any(axis=1).sum())

print("\nSaved:", output_file)
