from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

output_dir = Path("datasets/processed")
eda_dir = output_dir / "eda"
eda_dir.mkdir(parents=True, exist_ok=True)

results = pd.DataFrame([
    {
        "model": "Rainfall + Coordinates",
        "accuracy": 0.8073,
        "balanced_accuracy": 0.7909,
        "roc_auc": 0.8245,
        "flood_precision": 0.36,
        "flood_recall": 0.77,
        "flood_f1": 0.49
    },
    {
        "model": "Rainfall + Coordinates + Elevation",
        "accuracy": 0.8716,
        "balanced_accuracy": 0.7608,
        "roc_auc": 0.8598,
        "flood_precision": 0.47,
        "flood_recall": 0.62,
        "flood_f1": 0.53
    }
])

csv_file = output_dir / "pre_event_model_comparison.csv"
chart_file = eda_dir / "pre_event_model_comparison.png"

results.to_csv(csv_file, index=False)

metrics = [
    "accuracy",
    "balanced_accuracy",
    "roc_auc",
    "flood_precision",
    "flood_recall",
    "flood_f1"
]

ax = results.set_index("model")[metrics].T.plot(
    kind="bar",
    figsize=(11, 6)
)

ax.set_title("Pre-event Random Forest Model Comparison")
ax.set_ylabel("Score")
ax.set_xlabel("Evaluation Metrics")
ax.set_ylim(0, 1)
ax.legend(title="Model")
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.xticks(rotation=25, ha="right")
plt.tight_layout()
plt.savefig(chart_file, dpi=300)
plt.close()

print("PRE-EVENT MODEL COMPARISON")
print("--------------------------")
print(results.to_string(index=False))
print("\nSaved CSV:", csv_file)
print("Saved chart:", chart_file)