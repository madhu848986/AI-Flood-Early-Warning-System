
import os
import numpy as np
import pandas as pd

FOLD_DIR = "datasets/processed/spatial_cv_folds"

FEATURES = [
    "precipitation_mm_per_day",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "elevation_mean_m",
    "elevation_min_m",
    "elevation_max_m",
    "elevation_median_m",
    "elevation_range_m"
]

TARGET = "observed_flood_present"


def sigmoid(z):
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))


def train_logistic_regression(X, y, learning_rate=0.05,
                              epochs=3000, l2=0.01):
    n, p = X.shape

    weights = np.zeros(p)
    bias = 0.0

    positives = np.sum(y == 1)
    negatives = np.sum(y == 0)

    sample_weights = np.where(
        y == 1,
        n / (2 * positives),
        n / (2 * negatives)
    )

    for _ in range(epochs):
        probabilities = sigmoid(X @ weights + bias)

        errors = (probabilities - y) * sample_weights

        dw = (X.T @ errors) / n + l2 * weights
        db = np.sum(errors) / n

        weights -= learning_rate * dw
        bias -= learning_rate * db

    return weights, bias


def calculate_auc(y_true, scores):
    positive_scores = scores[y_true == 1]
    negative_scores = scores[y_true == 0]

    if len(positive_scores) == 0 or len(negative_scores) == 0:
        return np.nan

    comparisons = (
        positive_scores[:, None] - negative_scores[None, :]
    )

    return (
        np.sum(comparisons > 0)
        + 0.5 * np.sum(comparisons == 0)
    ) / comparisons.size


def calculate_metrics(y_true, probabilities):
    predictions = (probabilities >= 0.5).astype(int)

    tp = np.sum((y_true == 1) & (predictions == 1))
    tn = np.sum((y_true == 0) & (predictions == 0))
    fp = np.sum((y_true == 0) & (predictions == 1))
    fn = np.sum((y_true == 1) & (predictions == 0))

    accuracy = (tp + tn) / len(y_true)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    specificity = tn / (tn + fp) if tn + fp else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    balanced_accuracy = (recall + specificity) / 2
    auc = calculate_auc(y_true, probabilities)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "f1_score": f1,
        "balanced_accuracy": balanced_accuracy,
        "roc_auc": auc,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn
    }


all_results = []
all_predictions = []

print("NUMPY LOGISTIC REGRESSION")
print("=" * 60)

for fold in range(1, 6):
    train_file = os.path.join(
        FOLD_DIR, f"fold_{fold}_train.csv"
    )
    test_file = os.path.join(
        FOLD_DIR, f"fold_{fold}_test.csv"
    )

    train_df = pd.read_csv(train_file)
    test_df = pd.read_csv(test_file)

    X_train = train_df[FEATURES].to_numpy(dtype=float)
    y_train = train_df[TARGET].astype(int).to_numpy()

    X_test = test_df[FEATURES].to_numpy(dtype=float)
    y_test = test_df[TARGET].astype(int).to_numpy()

    # Standardize using training data only
    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0)
    std[std == 0] = 1

    X_train = (X_train - mean) / std
    X_test = (X_test - mean) / std

    # Train model
    weights, bias = train_logistic_regression(
        X_train, y_train
    )

    # Predict
    probabilities = sigmoid(X_test @ weights + bias)

    # Evaluate
    metrics = calculate_metrics(y_test, probabilities)
    metrics["fold"] = fold

    all_results.append(metrics)

    all_predictions.append(
        pd.DataFrame({
            "fold": fold,
            "actual": y_test,
            "predicted_probability": probabilities,
            "predicted_class": (probabilities >= 0.5).astype(int)
        })
    )

    print(f"\nFOLD {fold}")
    for name, value in metrics.items():
        if name != "fold":
            print(f"{name}: {value:.4f}" if isinstance(value, (float, np.floating))
                  else f"{name}: {value}")

# Save fold results
results_df = pd.DataFrame(all_results)

results_file = (
    "datasets/processed/"
    "spatial_logistic_regression_fold_metrics.csv"
)

results_df.to_csv(results_file, index=False)

# Save all out-of-fold predictions
predictions_df = pd.concat(all_predictions, ignore_index=True)

predictions_file = (
    "datasets/processed/"
    "spatial_logistic_regression_predictions.csv"
)

predictions_df.to_csv(predictions_file, index=False)

print("\n" + "=" * 60)
print("FIVE-FOLD SUMMARY")
print("=" * 60)

metric_columns = [
    "accuracy",
    "precision",
    "recall",
    "specificity",
    "f1_score",
    "balanced_accuracy",
    "roc_auc"
]

print(results_df[metric_columns].agg(["mean", "std"]).to_string())

print("\nSaved fold metrics:", results_file)
print("Saved predictions:", predictions_file)
