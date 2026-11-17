
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

file_path = Path(
    "datasets/processed/koshi_pre_event_ml_dataset.csv"
)

output_dir = Path("datasets/processed/eda")
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(file_path)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

features = [
    ("daily_rainfall_mm", "Daily Rainfall"),
    ("rainfall_3day_mm", "3-Day Rainfall"),
    ("rainfall_7day_mm", "7-Day Rainfall")
]

for ax, (feature, title) in zip(axes, features):

    scatter = ax.scatter(
        df["longitude"],
        df["latitude"],
        c=df[feature],
        s=18,
        cmap="viridis"
    )

    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    fig.colorbar(scatter, ax=ax, label="Rainfall (mm)")

plt.tight_layout()

output_file = output_dir / "pre_event_rainfall_spatial_coverage.png"

plt.savefig(output_file, dpi=300)
plt.close()

print("Saved:", output_file)
