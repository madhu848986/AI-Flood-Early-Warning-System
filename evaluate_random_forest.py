
import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

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

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

results = df.iloc[test_idx][
    ["latitude", "longitude"]
].copy()

results["actual_flood_label"] = y_test.values
results["predicted_flood_label"] = predictions
results["flood_probability"] = probabilities

results.to_csv(
    "datasets/processed/random_forest_predictions.csv",
    index=False
)

matrix = confusion_matrix(y_test, predictions)

display = ConfusionMatrixDisplay(
    confusion_matrix=matrix,
    display_labels=["No Flood", "Flood"]
)

display.plot()
plt.title("Random Forest - Confusion Matrix")
plt.tight_layout()

plt.savefig(
    "datasets/processed/eda/random_forest_confusion_matrix.png",
    dpi=300
)

plt.close()

print("Evaluation outputs saved successfully.")
print("Prediction records:", len(results))
print("Confusion matrix:")
print(matrix)
