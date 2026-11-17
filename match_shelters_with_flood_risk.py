
import pandas as pd
import numpy as np

shelter_file = "datasets/processed/koshi_shelter_candidates.csv"
prediction_file = "datasets/processed/koshi_all_grid_flood_predictions.csv"
output_file = "datasets/processed/koshi_shelter_risk_screening.csv"

shelters = pd.read_csv(shelter_file)
predictions = pd.read_csv(prediction_file)

def haversine(lat1, lon1, lat2, lon2):
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    return 6371 * 2 * np.arcsin(np.sqrt(a))

matched_rows = []

grid_latitudes = predictions["latitude"].to_numpy(dtype=float)
grid_longitudes = predictions["longitude"].to_numpy(dtype=float)

for _, shelter in shelters.iterrows():

    distances = haversine(
        float(shelter["latitude"]),
        float(shelter["longitude"]),
        grid_latitudes,
        grid_longitudes
    )

    nearest_index = int(np.argmin(distances))
    nearest = predictions.iloc[nearest_index]

    row = shelter.to_dict()

    row["nearest_grid_latitude"] = nearest["latitude"]
    row["nearest_grid_longitude"] = nearest["longitude"]
    row["distance_to_grid_km"] = float(distances[nearest_index])

    row["flood_probability"] = nearest["flood_probability"]
    row["risk_category"] = nearest["risk_category"]
    row["elevation_mean_m"] = nearest["elevation_mean_m"]

    matched_rows.append(row)

result = pd.DataFrame(matched_rows)

result.to_csv(output_file, index=False)

print("SHELTER RISK SCREENING COMPLETED")
print("Total shelters:", len(result))
print("Matched shelters:", result["flood_probability"].notna().sum())

print(
    "Average grid distance (km):",
    round(result["distance_to_grid_km"].mean(), 4)
)

print(
    "Maximum grid distance (km):",
    round(result["distance_to_grid_km"].max(), 4)
)

print("\nRISK CATEGORY COUNTS:")
print(result["risk_category"].value_counts(dropna=False))

print("\nSaved:", output_file)
