
import pandas as pd

input_file = "datasets/processed/koshi_shelter_risk_screening.csv"
output_file = "datasets/processed/koshi_shelter_screening_filtered.csv"

df = pd.read_csv(input_file)

MAX_DISTANCE_KM = 10

df["spatial_match_status"] = df["distance_to_grid_km"].apply(
    lambda distance:
        "Preliminary match"
        if distance <= MAX_DISTANCE_KM
        else "Insufficient spatial coverage"
)

df["screening_risk_category"] = df["risk_category"]

df.loc[
    df["distance_to_grid_km"] > MAX_DISTANCE_KM,
    "screening_risk_category"
] = "Not assessed"

df.to_csv(output_file, index=False)

print("SHELTER SPATIAL SCREENING")
print("Total shelters:", len(df))

print("\nSpatial match status:")
print(df["spatial_match_status"].value_counts().to_string())

print("\nScreening risk categories:")
print(df["screening_risk_category"].value_counts().to_string())

print("\nSaved:", output_file)
