from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path("datasets/processed")
EDA_DIR = DATA_DIR / "eda"
EDA_DIR.mkdir(parents=True, exist_ok=True)

files = {
    "Coordinates only":
        DATA_DIR / "coordinate_only_validation_results.csv",

    "Rainfall + Coordinates":
        DATA_DIR / "repeated_spatial_validation_results.csv",

    "Rainfall + Coordinates + Elevation":
        DATA_DIR / "repeated_spatial_validation_results.csv"
}

frames = []

for model_name, file_path in files.items():
    df = pd.read_csv(file_path)

    if model_name != "Coordinates only":
        df = df[df["model"] == model_name]

    df["model"] = model_name
    frames.append(df)

all_results = pd.concat(frames, ignore_index=True)

metrics = [
    "accuracy",
    "balanced_accuracy",
    "roc_auc",
    "flood_precision",
    "flood_recall",
    "flood_f1"
]

summary = all_results.groupby("model")[metrics].agg(["mean", "std"])

output_file = DATA_DIR / "all_pre_event_models_comparison.csv"
chart_file = EDA_DIR / "all_pre_event_models_comparison.png"

summary.to_csv(output_file)

means = all_results.groupby("model")[metrics].mean()

ax = means.T.plot(
    kind="bar",
    figsize=(12, 6)
)

ax.set_title("Pre-event Model Comparison - 10 Spatial Splits")
ax.set_ylabel("Mean Score")
ax.set_xlabel("Evaluation Metrics")
ax.set_ylim(0, 1)
ax.legend(title="Model")
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.xticks(rotation=25, ha="right")
plt.tight_layout()
plt.savefig(chart_file, dpi=300)
plt.close()

print("ALL PRE-EVENT MODEL COMPARISON")
print("--------------------------------")
print(summary.round(4).to_string())

print("\nSaved comparison:", output_file)
print("Saved chart:", chart_file)