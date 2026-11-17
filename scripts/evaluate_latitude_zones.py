
import numpy as np
import pandas as pd

file_path = "datasets/processed/koshi_oct13_model_features_cs_v4_latitude_zones.csv"

df = pd.read_csv(file_path)

features = [
    "precipitation_mm_per_day",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "elevation_mean_m",
    "elevation_min_m",
    "elevation_max_m",
    "elevation_median_m",
    "elevation_range_m"
]

X = df[features].to_numpy(dtype=float)
y = df["observed_flood_present"].to_numpy(dtype=int)
zones = df["spatial_zone"].to_numpy()

results = []
prediction_records = []

print("LEAVE-ONE-ZONE-OUT EVALUATION")
print("=" * 65)

for zone in sorted(np.unique(zones)):

    test = zones == zone
    train = ~test

    X_train = X[train]
    X_test = X[test]

    y_train = y[train]
    y_test = y[test]

    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0)
    std[std == 0] = 1

    X_train = (X_train - mean) / std
    X_test = (X_test - mean) / std

    A_train = np.column_stack([np.ones(len(X_train)), X_train])
    A_test = np.column_stack([np.ones(len(X_test)), X_test])

    n_positive = np.sum(y_train == 1)
    n_negative = np.sum(y_train == 0)

    if n_positive == 0 or n_negative == 0:
        print("Cannot train zone", zone, "- one class is missing.")
        continue

    weights = np.where(
        y_train == 1,
        len(y_train) / (2 * n_positive),
        len(y_train) / (2 * n_negative)
    )

    beta = np.zeros(A_train.shape[1])

    for epoch in range(3000):

        scores = np.clip(A_train @ beta, -30, 30)
        train_probabilities = 1 / (1 + np.exp(-scores))

        gradient = A_train.T @ (
            weights * (train_probabilities - y_train)
        ) / len(y_train)

        gradient[1:] += 0.01 * beta[1:]

        beta -= 0.05 * gradient

    scores = np.clip(A_test @ beta, -30, 30)
    probabilities = 1 / (1 + np.exp(-scores))

    predictions = (probabilities >= 0.50).astype(int)

    # Store predictions and actual labels
    zone_predictions = df.loc[test, [
        "date",
        "latitude",
        "longitude",
        "observed_flood_present",
        "spatial_zone"
    ]].copy()

    zone_predictions["predicted_probability"] = probabilities
    zone_predictions["predicted_class"] = predictions

    zone_predictions["correct_prediction"] = (
        zone_predictions["observed_flood_present"]
        == zone_predictions["predicted_class"]
    )

    prediction_records.append(zone_predictions)

    # Confusion matrix
    tp = int(np.sum((predictions == 1) & (y_test == 1)))
    fp = int(np.sum((predictions == 1) & (y_test == 0)))
    tn = int(np.sum((predictions == 0) & (y_test == 0)))
    fn = int(np.sum((predictions == 0) & (y_test == 1)))

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    specificity = tn / (tn + fp) if tn + fp else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    balanced_accuracy = (recall + specificity) / 2

    positive_scores = probabilities[y_test == 1]
    negative_scores = probabilities[y_test == 0]

    if len(positive_scores) and len(negative_scores):

        comparisons = [
            1 if p > n else 0.5 if p == n else 0
            for p in positive_scores
            for n in negative_scores
        ]

        roc_auc = float(np.mean(comparisons))

    else:
        roc_auc = float("nan")

    results.append({
        "zone": zone,
        "cells": len(y_test),
        "positive": int(np.sum(y_test == 1)),
        "negative": int(np.sum(y_test == 0)),
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "balanced_accuracy": balanced_accuracy,
        "roc_auc": roc_auc
    })

    print("\nZone:", zone)
    print("Test cells:", len(y_test))

    print(
        "Confusion matrix: TP =", tp,
        "FP =", fp,
        "TN =", tn,
        "FN =", fn
    )

    print("Precision: {:.3f}".format(precision))
    print("Recall: {:.3f}".format(recall))
    print("F1-score: {:.3f}".format(f1))
    print("Balanced accuracy: {:.3f}".format(balanced_accuracy))
    print("ROC-AUC: {:.3f}".format(roc_auc))

    print("-" * 65)


# Save prediction records
if prediction_records:

    prediction_df = pd.concat(
        prediction_records,
        ignore_index=True
    )

    prediction_path = (
        "datasets/processed/"
        "koshi_oct13_latitude_zone_predictions.csv"
    )

    prediction_df.to_csv(prediction_path, index=False)

    print("\nPredictions saved:", prediction_path)


# Save evaluation metrics
if results:

    results_df = pd.DataFrame(results)

    results_path = (
        "datasets/processed/"
        "koshi_oct13_latitude_zone_metrics.csv"
    )

    results_df.to_csv(results_path, index=False)

    print("\nFINAL SUMMARY")
    print(results_df.round(3).to_string(index=False))

    print("\nMetrics saved:", results_path)
