
import pandas as pd

input_file = "datasets/raw/osm/koshi/koshi_potential_facilities.csv"
coordinate_file = "datasets/processed/koshi_facilities_with_coordinates.csv"

output_file = "datasets/processed/koshi_shelter_candidates.csv"

raw = pd.read_csv(input_file)
coords = pd.read_csv(coordinate_file)

tags = raw["other_tags"].fillna("")

amenity = tags.str.extract(
    r'"amenity"=>"([^"]+)"',
    expand=False
)

social = tags.str.extract(
    r'"social_facility"=>"([^"]+)"',
    expand=False
)

raw["shelter_source"] = ""

raw.loc[amenity.eq("shelter"), "shelter_source"] = "amenity=shelter"
raw.loc[social.eq("shelter"), "shelter_source"] = "social_facility=shelter"

mask = raw["shelter_source"].ne("")

shelters = coords.loc[mask].copy()
shelters["shelter_source"] = raw.loc[mask, "shelter_source"].values

shelters.to_csv(output_file, index=False)

print("COMPLETE SHELTER CANDIDATE DATASET")
print("Total candidates:", len(shelters))
print("\nSource breakdown:")
print(shelters["shelter_source"].value_counts().to_string())

print("\nNamed:", shelters["name"].notna().sum())
print("Unnamed:", shelters["name"].isna().sum())
print("Missing coordinates:",
      shelters[["longitude", "latitude"]].isna().any(axis=1).sum())

print("\nSaved:", output_file)
