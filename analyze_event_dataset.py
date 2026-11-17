
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

input_file = Path(
    "datasets/processed/koshi_event_analysis_dataset.csv"
)

output_dir = Path("datasets/processed/eda")
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_file)

print("EVENT DATASET ANALYSIS")
print("=" * 45)

print("Total grid cells:", len(df))

print("\nFlood distribution:")
print(df["flood_label"].value_counts())

print("\nRainfall statistics by flood label:")
print(
    df.groupby("flood_label")[
        [
            "daily_rainfall_mm",
            "rainfall_3day_mm",
            "rainfall_7day_mm"
        ]
    ].mean().round(3)
)

print("\nFlood pixel ratio statistics:")
print(
    df.groupby("flood_label")[
        "flood_pixel_ratio"
    ].describe().round(4)
)

# Graph 1: Spatial flood distribution
plt.figure(figsize=(10, 7))

plt.scatter(
    df[df["flood_label"] == 0]["longitude"],
    df[df["flood_label"] == 0]["latitude"],
    label="No unusual flood pixels",
    s=25
)

plt.scatter(
    df[df["flood_label"] == 1]["longitude"],
    df[df["flood_label"] == 1]["latitude"],
    label="Unusual flood pixels observed",
    s=25
)

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("MODIS Flood Observation Distribution - Koshi Basin")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    output_dir / "flood_spatial_distribution.png",
    dpi=300
)
plt.close()

# Graph 2: Daily rainfall comparison
plt.figure(figsize=(8, 6))

df.boxplot(
    column="daily_rainfall_mm",
    by="flood_label"
)

plt.xlabel("Flood label (0 = No, 1 = Yes)")
plt.ylabel("Daily rainfall (mm)")
plt.title("Daily Rainfall by Observed Flood Label")
plt.suptitle("")
plt.tight_layout()

plt.savefig(
    output_dir / "daily_rainfall_comparison.png",
    dpi=300
)
plt.close()

# Graph 3: Seven-day rainfall and flood pixel ratio
plt.figure(figsize=(8, 6))

plt.scatter(
    df["rainfall_7day_mm"],
    df["flood_pixel_ratio"],
    alpha=0.65
)

plt.xlabel("Seven-day rainfall accumulation (mm)")
plt.ylabel("Unusual flood pixel ratio")
plt.title("Seven-day Rainfall vs Observed Flood Pixel Ratio")
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    output_dir / "rainfall_flood_relationship.png",
    dpi=300
)
plt.close()

print("\nEDA completed successfully.")
print("Graphs saved in:", output_dir)
