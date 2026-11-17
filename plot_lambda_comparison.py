
import pandas as pd
import matplotlib.pyplot as plt
import os

INPUT_FILE = "datasets/processed/20_pair_lambda_evaluation.csv"
OUTPUT_FILE = "datasets/processed/eda/lambda_comparison.png"

df = pd.read_csv(INPUT_FILE)

summary = df.groupby("lambda").agg(
    average_risk_reduction=("risk_percent", "mean"),
    average_extra_distance=("extra_km", "mean"),
    improved_pairs=("improved", "sum"),
    total_pairs=("pair", "nunique")
).reset_index()

print("\nLAMBDA COMPARISON SUMMARY")
print(summary.to_string(index=False))

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

labels = [f"Lambda {int(x)}" for x in summary["lambda"]]

axes[0].bar(labels, summary["average_risk_reduction"])
axes[0].set_title("Average Estimated Risk Reduction")
axes[0].set_ylabel("Risk reduction (%)")
axes[0].grid(axis="y", alpha=0.3)

axes[1].bar(labels, summary["average_extra_distance"])
axes[1].set_title("Average Additional Route Distance")
axes[1].set_ylabel("Additional distance (km)")
axes[1].grid(axis="y", alpha=0.3)

fig.suptitle("Flood-Aware Routing: Lambda 5 vs Lambda 10")
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
plt.show()

print("\nChart saved:", OUTPUT_FILE)
print("LAMBDA COMPARISON COMPLETED")
