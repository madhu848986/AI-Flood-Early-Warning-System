
from pathlib import Path

import joblib
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path("datasets/processed")
EDA_DIR = DATA_DIR / "eda"

INPUT_FILE = DATA_DIR / "koshi_pre_event_ml_with_elevation.csv"
MODEL_FILE = DATA_DIR / "final_koshi_random_forest.pkl"

PREDICTION_FILE = DATA_DIR / "final_koshi_flood_predictions.csv"
OUTPUT_FILE = EDA_DIR / "koshi_flood_risk_map.png"

THRESHOLD = 0.40

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude",
    "elevation_mean_m"
]

df = pd.read_csv(INPUT_FILE)
model = joblib.load(MODEL_FILE)

X = df[features]

df["flood_probability"] = model.predict_proba(X)[:, 1]

df["risk_category"] = df["flood_probability"].apply(
    lambda probability:
        "High Risk" if probability >= THRESHOLD
        else "Lower Risk"
)

df.to_csv(PREDICTION_FILE, index=False)

EDA_DIR.mkdir(parents=True, exist_ok=True)

colors = {
    "Lower Risk": "lightgreen",
    "High Risk": "red"
}

plt.figure(figsize=(11, 8))

for category, color in colors.items():
    subset = df[df["risk_category"] == category]

    plt.scatter(
        subset["longitude"],
        subset["latitude"],
        c=color,
        label=category,
        s=35,
        alpha=0.75,
        edgecolors="black",
        linewidths=0.2
    )

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.title(
    "Koshi Basin - Experimental Flood Risk Classification\n"
    "Final Random Forest Model (Threshold = 0.40)"
)

plt.legend(title="Predicted Category")
plt.grid(alpha=0.25)
plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("FLOOD RISK PREDICTION COMPLETED")
print("--------------------------------")
print("Total grid cells:", len(df))
print("\nPredicted risk category counts:")
print(df["risk_category"].value_counts())

print("\nMean flood probability:", round(df["flood_probability"].mean(), 4))
print("\nPrediction file:", PREDICTION_FILE)
print("Map file:", OUTPUT_FILE)
