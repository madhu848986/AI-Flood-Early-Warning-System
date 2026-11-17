import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    classification_report,
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

THRESHOLD = 0.40

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

predictions = (
    probabilities >= THRESHOLD
).astype(int)

results = df.iloc[test_idx][
    ["latitude", "longitude"]
].copy()

results["actual_flood_label"] = y_test.values
results["predicted_flood_label"] = predictions
results["flood_probability"] = probabilities
results["classification_threshold"] = THRESHOLD

results.to_csv(
    "datasets/processed/random_forest_threshold_040_predictions.csv",
    index=False
)

matrix = confusion_matrix(y_test, predictions)

print("Selected Threshold:", THRESHOLD)
print("Accuracy:", accuracy_score(y_test, predictions))
print(
    "Balanced Accuracy:",
    balanced_accuracy_score(y_test, predictions)
)
print(
    "Flood Precision:",
    precision_score(y_test, predictions, zero_division=0)
)
print(
    "Flood Recall:",
    recall_score(y_test, predictions, zero_division=0)
)
print(
    "Flood F1:",
    f1_score(y_test, predictions, zero_division=0)
)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        target_names=["No Flood", "Flood"],
        zero_division=0
    )
)

print("Confusion Matrix:")
print(matrix)

display = ConfusionMatrixDisplay(
    confusion_matrix=matrix,
    display_labels=["No Flood", "Flood"]
)

display.plot()
plt.title("Random Forest - Threshold 0.40")
plt.tight_layout()

plt.savefig(
    "datasets/processed/eda/random_forest_threshold_040_confusion_matrix.png",
    dpi=300
)

plt.close()

print("\nSelected threshold evaluation completed.")