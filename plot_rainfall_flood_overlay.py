
import os
import pandas as pd
import matplotlib.pyplot as plt

# Input dataset paths
rainfall_path = "datasets/processed/koshi_pre_event_ml_dataset.csv"
flood_path = "datasets/processed/koshi_pre_event_flood_dataset.csv"

# Load datasets
rainfall = pd.read_csv(rainfall_path)
flood = pd.read_csv(flood_path)

# Validate required columns
required_rainfall = [
    "latitude",
    "longitude",
    "rainfall_7day_mm"
]

required_flood = [
    "latitude",
    "longitude",
    "flood_label"
]

for column in required_rainfall:
    if column not in rainfall.columns:
        raise ValueError(f"Missing rainfall column: {column}")

for column in required_flood:
    if column not in flood.columns:
        raise ValueError(f"Missing flood column: {column}")

# Create coordinate keys for matching
rainfall["latitude_key"] = rainfall["latitude"].round(4)
rainfall["longitude_key"] = rainfall["longitude"].round(4)

flood["latitude_key"] = flood["latitude"].round(4)
flood["longitude_key"] = flood["longitude"].round(4)

# Select only required rainfall columns before merging.
# This avoids duplicate flood_label columns.
merged = rainfall[
    [
        "latitude_key",
        "longitude_key",
        "latitude",
        "longitude",
        "rainfall_7day_mm"
    ]
].merge(
    flood[
        [
            "latitude_key",
            "longitude_key",
            "flood_label"
        ]
    ],
    on=["latitude_key", "longitude_key"],
    how="inner",
    validate="one_to_one"
)

# Check matching results
if merged.empty:
    raise ValueError("No matching grid cells found.")

if merged["flood_label"].isna().any():
    raise ValueError("Missing flood labels found after merging.")

# Separate flood and non-flood cells
flooded = merged[merged["flood_label"] == 1]
non_flooded = merged[merged["flood_label"] == 0]

# Print summary
print("\nRAINFALL AND FLOOD OVERLAY SUMMARY")
print("---------------------------------")
print("Total rainfall grid cells:", len(rainfall))
print("Matched labelled cells:", len(merged))
print("Flood-labelled cells:", len(flooded))
print("Non-flood-labelled cells:", len(non_flooded))

print("\n7-DAY RAINFALL STATISTICS BY FLOOD LABEL")
print("----------------------------------------")

print(
    merged.groupby("flood_label")["rainfall_7day_mm"]
    .agg(["count", "mean", "median", "std", "min", "max"])
)

# Create plot
fig, ax = plt.subplots(figsize=(12, 9))

# Background: 7-day rainfall across all rainfall grid cells
background = ax.scatter(
    rainfall["longitude"],
    rainfall["latitude"],
    c=rainfall["rainfall_7day_mm"],
    cmap="viridis",
    s=22,
    alpha=0.85,
    label="Rainfall grid cells"
)

# Non-flood-labelled cells
ax.scatter(
    non_flooded["longitude"],
    non_flooded["latitude"],
    facecolors="none",
    edgecolors="blue",
    s=42,
    linewidths=0.9,
    label="Non-flood-labelled cells"
)

# Flood-labelled cells
ax.scatter(
    flooded["longitude"],
    flooded["latitude"],
    marker="x",
    color="red",
    s=48,
    linewidths=1.5,
    label="Flood-labelled cells"
)

# Colorbar
colorbar = plt.colorbar(background, ax=ax)
colorbar.set_label("7-day rainfall (mm)")

# Labels and title
ax.set_title(
    "Pre-event 7-day Rainfall with Flood-label Overlay\n"
    "Koshi Basin | 6–12 October 2021",
    fontsize=13
)

ax.set_xlabel("Longitude (°E)")
ax.set_ylabel("Latitude (°N)")

ax.legend(loc="best")
ax.grid(alpha=0.2)

plt.tight_layout()

# Save output
output_dir = "datasets/processed/eda"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(
    output_dir,
    "pre_event_rainfall_flood_overlay.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nOverlay map saved successfully:")
print(output_path)
