
from pathlib import Path

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score
)

DATA_DIR = Path("datasets/processed")

rainfall_file = DATA_DIR / "koshi_pre_event_ml_dataset.csv"
elevation_file = DATA_DIR / "koshi_pre_event_ml_with_elevation.csv"

OUTPUT_FILE = DATA_DIR / "three_models_1degree_results.csv"
SUMMARY_FILE = DATA_DIR / "three_models_1degree_summary.csv"

rainfall_df = pd.read_csv(rainfall_file)
elevation_df = pd.read_csv(elevation_file)

target = "flood_label"

if len(rainfall_df) != len(elevation_df):
    raise ValueError("The datasets have different record counts.")

if not rainfall_df[["latitude", "longitude", target]].equals(
    elevation_df[["latitude", "longitude", target]]
):
    raise ValueError("Grid cells or labels do not match.")

coordinate_features = [
    "latitude",
    "longitude"
]

rainfall_features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude"
]

elevation_features = rainfall_features + [
    "elevation_mean_m"
]

datasets = {
    "Coordinates only": (
        rainfall_df,
        coordinate_features
    ),
    "Rainfall + Coordinates": (
        rainfall_df,
        rainfall_features
    ),
    "Rainfall + Coordinates + Elevation": (
        elevation_df,
        elevation_features
    )
}

# Create 1-degree spatial blocks.
groups = (
    (rainfall_df["latitude"] // 1.0).astype(int).astype(str)
    + "_"
    + (rainfall_df["longitude"] // 1.0).astype(int).astype(str)
)

splitter = GroupShuffleSplit(
    n_splits=20,
    test_size=0.25,
    random_state=42
)

results = []

for split_number, (train_index, test_index) in enumerate(
    splitter.split(rainfall_df, rainfall_df[target], groups),
    start=1
):

    y_train = rainfall_df.iloc[train_index][target]
    y_test = rainfall_df.iloc[test_index][target]

    if y_train.nunique() != 2 or y_test.nunique() != 2:
        print(f"Split {split_number}: skipped; one class is missing.")
        continue

    for model_name, (data, features) in datasets.items():

        X_train = data.iloc[train_index][features]
        X_test = data.iloc[test_index][features]

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

        results.append({
            "split": split_number,
            "model": model_name,
            "training_records": len(train_index),
            "testing_records": len(test_index),
            "test_flood_cells": int(y_test.sum()),
            "accuracy": accuracy_score(y_test, predictions),
            "balanced_accuracy": balanced_accuracy_score(
                y_test, predictions
            ),
            "roc_auc": roc_auc_score(y_test, probabilities),
            "flood_precision": precision_score(
                y_test, predictions, zero_division=0
            ),
            "flood_recall": recall_score(
                y_test, predictions, zero_division=0
            ),
            "flood_f1": f1_score(
                y_test, predictions, zero_division=0
            )
        })

    print(f"Completed split {split_number}")

if not results:
    raise ValueError("No valid spatial splits were available.")

results_df = pd.DataFrame(results)

results_df.to_csv(OUTPUT_FILE, index=False)

metrics = [
    "accuracy",
    "balanced_accuracy",
    "roc_auc",
    "flood_precision",
    "flood_recall",
    "flood_f1"
]

summary = results_df.groupby("model")[metrics].agg(
    ["mean", "std"]
)

summary.to_csv(SUMMARY_FILE)

print("\nTHREE-MODEL 1-DEGREE SPATIAL VALIDATION")
print("--------------------------------------")
print("Valid splits:", results_df["split"].nunique())
print("Model evaluations:", len(results_df))

print("\nMEAN AND STANDARD DEVIATION")
print(summary.round(4).to_string())

print("\nSaved detailed results:", OUTPUT_FILE)
print("Saved summary:", SUMMARY_FILE)
