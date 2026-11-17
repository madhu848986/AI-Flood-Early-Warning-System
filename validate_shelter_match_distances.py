
import pandas as pd

file = "datasets/processed/koshi_shelter_risk_screening.csv"
df = pd.read_csv(file)

distance = df["distance_to_grid_km"]

print("SHELTER MATCHING DISTANCE VALIDATION")
print("Total shelters:", len(df))

print("\nDISTANCE STATISTICS")
print(distance.describe().round(3))

print("\nDISTANCE GROUPS")
print("0–5 km:", ((distance >= 0) & (distance <= 5)).sum())
print("5–10 km:", ((distance > 5) & (distance <= 10)).sum())
print("10–20 km:", ((distance > 10) & (distance <= 20)).sum())
print("20–30 km:", ((distance > 20) & (distance <= 30)).sum())
print("Above 30 km:", (distance > 30).sum())

print("\nMATCHES ABOVE 20 KM")

columns = [
    "osm_id",
    "name",
    "amenity_type",
    "latitude",
    "longitude",
    "distance_to_grid_km",
    "risk_category"
]

print(
    df.loc[distance > 20, columns]
    .sort_values("distance_to_grid_km", ascending=False)
    .to_string(index=False)
)
