from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)

INPUT_FILE = Path(
    "datasets/processed/koshi_pre_event_ml_dataset.csv"
)

OUTPUT_DIR = Path("datasets/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude"
]

X = df[features]
y = df["flood_label"]

groups = (
    (df["latitude"] // 0.5).astype(int).astype(str)
    + "_"
    + (df["longitude"] // 0.5).astype(int).astype(str)
)

splitter = GroupShuffleSplit(
    n_splits=10,
    test_size=0.25,
    random_state=42
)

selected_split = None

for train_index, test_index in splitter.split(X, y, groups):
    if (
        y.iloc[train_index].nunique() == 2
        and y.iloc[test_index].nunique() == 2
    ):
        selected_split = (train_index, test_index)
        break

if selected_split is None:
    raise ValueError("Could not find a spatial split containing both classes.")

train_index, test_index = selected_split

X_train = X.iloc[train_index]
X_test = X.iloc[test_index]

y_train = y.iloc[train_index]
y_test = y.iloc[test_index]

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, predictions)
balanced_accuracy = balanced_accuracy_score(y_test, predictions)
roc_auc = roc_auc_score(y_test, probabilities)

print("PRE-EVENT RANDOM FOREST RESULTS")
print("--------------------------------")
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("Training flood cells:", int(y_train.sum()))
print("Testing flood cells:", int(y_test.sum()))

print("\nEvaluation Metrics")
print("Accuracy:", round(accuracy, 4))
print("Balanced Accuracy:", round(balanced_accuracy, 4))
print("ROC-AUC:", round(roc_auc, 4))

print("\nConfusion Matrix")
print(confusion_matrix(y_test, predictions))

print("\nClassification Report")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
}).sort_values(
    by="importance",
    ascending=False
)

print("\nFeature Importance")
print(importance.to_string(index=False))

model_file = OUTPUT_DIR / "pre_event_random_forest.pkl"
prediction_file = OUTPUT_DIR / "pre_event_random_forest_predictions.csv"

joblib.dump(model, model_file)

results = df.iloc[test_index][
    ["latitude", "longitude", "flood_label"]
].copy()

results["predicted_label"] = predictions
results["flood_probability"] = probabilities

results.to_csv(prediction_file, index=False)

print("\nSaved model:", model_file)
print("Saved predictions:", prediction_file)