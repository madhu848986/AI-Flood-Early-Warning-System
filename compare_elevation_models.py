import pandas as pd
import matplotlib.pyplot as plt

results = pd.DataFrame({
    "Metric": [
        "Accuracy",
        "Balanced Accuracy",
        "ROC-AUC",
        "Flood Recall",
        "Flood F1-score"
    ],
    "Baseline": [
        0.8716,
        0.6943,
        0.8293,
        0.4615,
        0.4615
    ],
    "With Elevation": [
        0.8349,
        0.7400,
        0.8518,
        0.6154,
        0.4706
    ]
})

output_file = "datasets/processed/elevation_model_comparison.csv"

results.to_csv(output_file, index=False)

print("MODEL COMPARISON")
print(results.to_string(index=False))

print("\nSaved comparison:", output_file)

ax = results.set_index("Metric").plot(
    kind="bar",
    figsize=(10, 6)
)

ax.set_title("Random Forest: Baseline vs Elevation-Enhanced")
ax.set_ylabel("Score")
ax.set_ylim(0, 1)
ax.set_xlabel("Evaluation Metrics")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()

chart_file = "datasets/processed/eda/elevation_model_comparison.png"
plt.savefig(chart_file, dpi=300)
plt.close()

print("Comparison chart saved:", chart_file)