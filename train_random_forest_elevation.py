import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)

INPUT_FILE = "datasets/processed/koshi_ml_dataset_with_elevation.csv"
MODEL_FILE = "datasets/processed/random_forest_elevation.pkl"

df = pd.read_csv(INPUT_FILE)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude",
    "elevation_m"
]

X = df[features]
y = df["flood_label"]

df["spatial_group"] = (
    (df["latitude"] // 0.5).astype(int).astype(str)
    + "_"
    + (df["longitude"] // 0.5).astype(int).astype(str)
)

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

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("ELEVATION-ENHANCED RANDOM FOREST RESULTS")
print("----------------------------------------")

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("Balanced Accuracy:", balanced_accuracy_score(y_test, y_pred))
print("ROC-AUC:", roc_auc_score(y_test, y_prob))

print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nFeature Importances:")
importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print(importance)

joblib.dump(model, MODEL_FILE)

print("\nModel saved at:", MODEL_FILE)

predictions = pd.DataFrame({
    "actual_label": y_test.values,
    "predicted_label": y_pred,
    "flood_probability": y_prob
})

predictions.to_csv(
    "datasets/processed/random_forest_elevation_predictions.csv",
    index=False
)

print("Predictions saved successfully.")