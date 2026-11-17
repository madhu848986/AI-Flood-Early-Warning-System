
import pandas as pd

file = "datasets/raw/osm/koshi/koshi_potential_facilities.csv"

df = pd.read_csv(file)

tags = df["other_tags"].fillna("")

print("AMENITY TAG COUNTS")
print("------------------")

amenity = tags.str.extract(
    r'"amenity"=>"([^"]+)"',
    expand=False
)

print(amenity.value_counts(dropna=False).to_string())

print("\nSOCIAL FACILITY TAG COUNTS")
print("--------------------------")

social = tags.str.extract(
    r'"social_facility"=>"([^"]+)"',
    expand=False
)

print(social.value_counts(dropna=False).head(20).to_string())

print("\nEMERGENCY TAG COUNTS")
print("--------------------")

emergency = tags.str.extract(
    r'"emergency"=>"([^"]+)"',
    expand=False
)

print(emergency.value_counts(dropna=False).to_string())
