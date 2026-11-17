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

INPUT_FILE = DATA_DIR / "koshi_pre_event_ml_dataset.csv"

OUTPUT_FILE = DATA_DIR / "coordinate_only_validation_results.csv"

df = pd.read_csv(INPUT_FILE)

features = [
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

results = []

for split_number, (train_index, test_index) in enumerate(
    splitter.split(X, y, groups),
    start=1
):

    X_train = X.iloc[train_index]
    X_test = X.iloc[test_index]

    y_train = y.iloc[train_index]
    y_test = y.iloc[test_index]

    if y_train.nunique() != 2 or y_test.nunique() != 2:
        print(f"Split {split_number}: skipped.")
        continue

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
    raise ValueError("No valid spatial splits found.")

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

print("\nCOORDINATE-ONLY BASELINE")
print("------------------------")
print("Valid splits:", len(results_df))

print("\nMean metrics:")
print(results_df[metrics].mean().round(4))

print("\nStandard deviation:")
print(results_df[metrics].std().round(4))

print("\nSaved:", OUTPUT_FILE)