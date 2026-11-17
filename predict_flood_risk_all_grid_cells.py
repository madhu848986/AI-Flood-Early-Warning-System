
import pandas as pd
import joblib

input_file = "datasets/processed/koshi_all_grid_elevation.csv"
model_file = "datasets/processed/final_koshi_random_forest.pkl"
output_file = "datasets/processed/koshi_all_grid_flood_predictions.csv"

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude",
    "elevation_mean_m"
]

df = pd.read_csv(input_file)

if df[features].isna().any().any():
    raise ValueError("Missing model features detected")

model = joblib.load(model_file)

X = df[features]

df["flood_probability"] = model.predict_proba(X)[:, 1]

df["risk_category"] = df["flood_probability"].apply(
    lambda p: "High Risk" if p >= 0.40 else "Lower Risk"
)

df.to_csv(output_file, index=False)

print("FULL GRID FLOOD PREDICTION COMPLETED")
print("Total grid cells:", len(df))

print("\nRisk categories:")
print(df["risk_category"].value_counts().to_string())

print("\nFlood probability statistics:")
print(df["flood_probability"].describe().round(4))

print("\nSaved:", output_file)
