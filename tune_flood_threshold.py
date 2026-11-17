import pandas as pd
import joblib

from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

df = pd.read_csv(
    "datasets/processed/koshi_ml_dataset.csv"
)

df["spatial_group"] = (
    (df["latitude"] // 0.5).astype(int).astype(str)
    + "_"
    + (df["longitude"] // 0.5).astype(int).astype(str)
)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude"
]

X = df[features]
y = df["flood_label"]
groups = df["spatial_group"]

splitter = GroupShuffleSplit(
    n_splits=10,
    test_size=0.25,
    random_state=42
)

for train_idx, test_idx in splitter.split(X, y, groups):
    if (
        y.iloc[train_idx].nunique() == 2
        and y.iloc[test_idx].nunique() == 2
    ):
        break
else:
    raise ValueError("No suitable spatial split found.")

X_test = X.iloc[test_idx]
y_test = y.iloc[test_idx]

model = joblib.load(
    "datasets/processed/random_forest_baseline.pkl"
)

probabilities = model.predict_proba(X_test)[:, 1]

results = []

for threshold in [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]:

    predictions = (
        probabilities >= threshold
    ).astype(int)

    results.append({
        "Threshold": threshold,
        "Accuracy": accuracy_score(y_test, predictions),
        "Balanced Accuracy": balanced_accuracy_score(
            y_test, predictions
        ),
        "Flood Precision": precision_score(
            y_test, predictions, zero_division=0
        ),
        "Flood Recall": recall_score(
            y_test, predictions, zero_division=0
        ),
        "Flood F1": f1_score(
            y_test, predictions, zero_division=0
        )
    })

comparison = pd.DataFrame(results)

comparison.to_csv(
    "datasets/processed/flood_threshold_comparison.csv",
    index=False
)

print(comparison.to_string(index=False))

print("\nThreshold comparison saved successfully.")