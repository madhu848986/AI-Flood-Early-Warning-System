
import pandas as pd
import numpy as np

from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    balanced_accuracy_score,
    roc_auc_score
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
    raise ValueError("No valid spatial split found.")

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]
y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

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

print("RANDOM FOREST BASELINE RESULTS")
print("=" * 45)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

print("\nAccuracy:", round(
    accuracy_score(y_test, predictions), 4
))

print("Balanced accuracy:", round(
    balanced_accuracy_score(y_test, predictions), 4
))

print("ROC-AUC:", round(
    roc_auc_score(y_test, probabilities), 4
))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
}).sort_values(
    "importance",
    ascending=False
)

print("\nFeature Importance:")
print(importance.to_string(index=False))

model_path = (
    "datasets/processed/"
    "random_forest_baseline.pkl"
)

import joblib
joblib.dump(model, model_path)

print("\nModel saved:", model_path)
