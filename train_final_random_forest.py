
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier

DATA_DIR = Path("datasets/processed")

INPUT_FILE = DATA_DIR / "koshi_pre_event_ml_with_elevation.csv"

MODEL_FILE = DATA_DIR / "final_koshi_random_forest.pkl"

IMPORTANCE_FILE = DATA_DIR / "final_rf_feature_importance.csv"

df = pd.read_csv(INPUT_FILE)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude",
    "elevation_mean_m"
]

X = df[features]
y = df["flood_label"]

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

joblib.dump(model, MODEL_FILE)

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
}).sort_values(
    "importance",
    ascending=False
)

importance.to_csv(IMPORTANCE_FILE, index=False)

print("FINAL RANDOM FOREST MODEL")
print("--------------------------")
print("Training records:", len(X))
print("Flood cells:", int(y.sum()))
print("Non-flood cells:", int((y == 0).sum()))

print("\nFEATURE IMPORTANCE")
print(importance.to_string(index=False))

print("\nSaved model:", MODEL_FILE)
print("Saved feature importance:", IMPORTANCE_FILE)
