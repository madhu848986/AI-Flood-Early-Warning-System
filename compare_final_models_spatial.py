
from pathlib import Path

import pandas as pd
import numpy as np

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

from xgboost import XGBClassifier


DATA_DIR = Path("datasets/processed")

INPUT_FILE = DATA_DIR / "koshi_pre_event_ml_with_elevation.csv"

RESULT_FILE = DATA_DIR / "final_spatial_model_results.csv"
SUMMARY_FILE = DATA_DIR / "final_spatial_model_summary.csv"

df = pd.read_csv(INPUT_FILE)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude",
    "elevation_mean_m"
]

target = "flood_label"

X = df[features]
y = df[target]

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

results = []

for split_number, (train_idx, test_idx) in enumerate(
    splitter.split(X, y, groups),
    start=1
):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    if y_train.nunique() != 2 or y_test.nunique() != 2:
        print(f"Split {split_number} skipped: missing class")
        continue

    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ),

        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            objective="binary:logistic",
            scale_pos_weight=(
                (y_train == 0).sum() / (y_train == 1).sum()
            ),
            random_state=42,
            n_jobs=-1
        )
    }

    for model_name, model in models.items():

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)[:, 1]

        results.append({
            "split": split_number,
            "model": model_name,
            "training_records": len(train_idx),
            "testing_records": len(test_idx),
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

results_df.to_csv(RESULT_FILE, index=False)

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

print("\nFINAL SPATIAL MODEL COMPARISON")
print("--------------------------------")

print("Valid spatial splits:", results_df["split"].nunique())

print("\nMEAN AND STANDARD DEVIATION")
print(summary.round(4).to_string())

print("\nSaved detailed results:", RESULT_FILE)
print("Saved summary:", SUMMARY_FILE)
