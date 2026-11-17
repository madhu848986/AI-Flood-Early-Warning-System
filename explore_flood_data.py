import pandas as pd
import matplotlib.pyplot as plt

path = "datasets/processed/koshi_model_analysis.csv"
df = pd.read_csv(path)

print("EXPLORATORY DATA ANALYSIS")
print("=" * 45)

print("\nRainfall statistics:")
print(df["precipitation_mm_per_day"].describe())

print("\nRainfall by date:")
print(
    df.groupby("date")["precipitation_mm_per_day"]
    .agg(["mean", "max", "min"])
)

print("\nObserved flood labels:")
print(df["observed_flood_present"].value_counts())

# Use one record per grid cell because the MODIS observation
# is repeated across both rainfall dates.
cells = df.drop_duplicates(
    subset=["latitude", "longitude"]
).copy()

print("\nUnique observed cells:", len(cells))
print("Cells with observed flood pixels:",
      int((cells["observed_flood_present"] == 1).sum()))

# Plot 1: rainfall distribution
plt.figure(figsize=(8, 5))
plt.hist(
    cells["precipitation_mm_per_day"],
    bins=30,
    edgecolor="black"
)
plt.xlabel("Daily rainfall (mm/day)")
plt.ylabel("Number of grid cells")
plt.title("Rainfall Distribution in the Selected Koshi Region")
plt.tight_layout()
plt.savefig(
    "datasets/processed/rainfall_distribution.png",
    dpi=300
)
plt.close()

# Plot 2: rainfall by provisional observed-flood label
plt.figure(figsize=(8, 5))

for label, group in cells.groupby("observed_flood_present"):
    name = "Flood-class pixels observed" if label == 1 else "No flood-class pixels observed"
    plt.hist(
        group["precipitation_mm_per_day"],
        bins=25,
        alpha=0.6,
        label=name
    )

plt.xlabel("Daily rainfall (mm/day)")
plt.ylabel("Number of grid cells")
plt.title("Rainfall by MODIS Observed-Flood Label")
plt.legend()
plt.tight_layout()
plt.savefig(
    "datasets/processed/rainfall_by_flood_label.png",
    dpi=300
)
plt.close()

print("\nGraphs saved:")
print("datasets/processed/rainfall_distribution.png")
print("datasets/processed/rainfall_by_flood_label.png")