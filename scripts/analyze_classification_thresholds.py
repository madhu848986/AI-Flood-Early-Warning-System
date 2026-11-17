
import numpy as np
import pandas as pd

input_file = (
    "datasets/processed/"
    "spatial_logistic_regression_predictions.csv"
)

output_file = (
    "datasets/processed/"
    "classification_threshold_analysis.csv"
)

df = pd.read_csv(input_file)

y_true = df["actual"].to_numpy(dtype=int)
scores = df["predicted_probability"].to_numpy(dtype=float)

thresholds = np.arange(0.1, 1.0, 0.1)

results = []

for threshold in thresholds:
    predictions = (scores >= threshold).astype(int)

    tp = np.sum((y_true == 1) & (predictions == 1))
    tn = np.sum((y_true == 0) & (predictions == 0))
    fp = np.sum((y_true == 0) & (predictions == 1))
    fn = np.sum((y_true == 1) & (predictions == 0))

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    specificity = tn / (tn + fp) if tn + fp else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    balanced_accuracy = (recall + specificity) / 2

    results.append({
        "threshold": round(threshold, 2),
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "f1_score": f1,
        "balanced_accuracy": balanced_accuracy
    })

results_df = pd.DataFrame(results)

results_df.to_csv(output_file, index=False)

print("\nCLASSIFICATION THRESHOLD ANALYSIS")
print("=" * 90)

print(results_df.round(4).to_string(index=False))

best_row = results_df.loc[
    results_df["f1_score"].idxmax()
]

print("\nHighest F1-score threshold:")
print(best_row.to_string())

print("\nSaved:", output_file)
