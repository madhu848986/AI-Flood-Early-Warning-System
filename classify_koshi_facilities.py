
import pandas as pd

input_file = "datasets/raw/osm/koshi/koshi_potential_facilities.csv"
output_file = "datasets/processed/koshi_classified_facilities.csv"

df = pd.read_csv(input_file)

tags = df["other_tags"].fillna("")

def extract_tag(key):
    return tags.str.extract(
        '"' + key + '"=>"([^"]+)"',
        expand=False
    )

df["amenity_type"] = extract_tag("amenity")
df["social_facility_type"] = extract_tag("social_facility")
df["emergency"] = extract_tag("emergency")

df["facility_category"] = df["amenity_type"]

df.loc[
    df["amenity_type"].eq("social_facility"),
    "facility_category"
] = df["social_facility_type"]

df["is_mapped_shelter"] = (
    df["amenity_type"].eq("shelter")
    | df["social_facility_type"].eq("shelter")
)

df["is_emergency_tagged"] = df["emergency"].eq("yes")

df.to_csv(output_file, index=False)

print("CLASSIFIED FACILITY DATASET CREATED")
print("Total features:", len(df))

print("\nFacility categories:")
print(df["facility_category"].value_counts(dropna=False))

print("\nExplicit shelter candidates:", df["is_mapped_shelter"].sum())
print("Emergency tagged features:", df["is_emergency_tagged"].sum())

print("\nSaved:", output_file)
