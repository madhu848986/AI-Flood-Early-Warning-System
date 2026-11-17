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

INPUT_CSV = (
    "datasets/processed/koshi_ml_dataset_with_zonal_elevation.csv"
)

MODEL_FILE = (
    "datasets/processed/random_forest_zonal_elevation.pkl"
)

PREDICTIONS_FILE = (
    "datasets/processed/random_forest_zonal_elevation_predictions.csv"
)

df = pd.read_csv(INPUT_CSV)

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

groups = (
    (df["latitude"] // 0.5).astype(str)
    + "_"
    + (df["longitude"] // 0.5).astype(str)
)

splitter = GroupShuffleSplit(
    n_splits=10,
    test_size=0.25,
    random_state=42
)

train_index, test_index = next(
    splitter.split(X, y, groups)
)

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

print("ZONAL ELEVATION RANDOM FOREST RESULTS")
print("------------------------------------")

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

print("\nAccuracy:", accuracy_score(y_test, predictions))
print(
    "Balanced Accuracy:",
    balanced_accuracy_score(y_test, predictions)
)
print("ROC-AUC:", roc_auc_score(y_test, probabilities))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

print("\nClassification Report:")
print(classification_report(y_test, predictions))

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
}).sort_values(
    by="importance",
    ascending=False
)

print("\nFEATURE IMPORTANCE")
print(importance.to_string(index=False))

importance.to_csv(
    "datasets/processed/zonal_elevation_feature_importance.csv",
    index=False
)

output = df.iloc[test_index].copy()
output["predicted_flood_label"] = predictions
output["flood_probability"] = probabilities

output.to_csv(PREDICTIONS_FILE, index=False)

joblib.dump(model, MODEL_FILE)

print("\nModel saved:", MODEL_FILE)
print("Predictions saved:", PREDICTIONS_FILE)