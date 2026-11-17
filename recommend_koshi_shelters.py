
import pandas as pd

input_file = "datasets/processed/koshi_shelter_screening_filtered.csv"
output_file = "datasets/processed/koshi_shelter_recommendations.csv"

print("Loading shelter data...", flush=True)

data = pd.read_csv(input_file)

required = [
    "osm_id",
    "longitude",
    "latitude",
    "flood_probability",
    "elevation_mean_m",
    "distance_to_grid_km"
]

if not all(column in data.columns for column in required):
    raise ValueError("Required shelter columns are missing")

data = data.dropna(subset=[
    "longitude",
    "latitude",
    "flood_probability"
]).copy()

data = data.sort_values(
    by=["flood_probability", "distance_to_grid_km"],
    ascending=[True, True]
).reset_index(drop=True)

data.insert(0, "recommendation_rank", range(1, len(data) + 1))

data["verification_status"] = "Field verification required"

data["recommendation_priority"] = data["risk_category"].map({
    "Lower Risk": "Higher verification priority",
    "High Risk": "Requires additional risk assessment"
})

data.to_csv(output_file, index=False)

print("\nSHELTER RECOMMENDATION MODULE COMPLETED")
print("Total candidates:", len(data))
print("\nPriority distribution:")
print(data["recommendation_priority"].value_counts())

print("\nTop 10 candidates for field verification:")
print(
    data[
        [
            "recommendation_rank",
            "osm_id",
            "longitude",
            "latitude",
            "flood_probability",
            "risk_category",
            "verification_status"
        ]
    ].head(10).to_string(index=False)
)

print("\nSaved:", output_file)
