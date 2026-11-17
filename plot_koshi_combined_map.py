import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

grid_file = "datasets/processed/koshi_all_grid_flood_predictions.csv"
shelter_file = "datasets/processed/koshi_shelter_recommendations.csv"
output_file = "datasets/processed/koshi_combined_flood_shelter_map.png"

print("Loading flood-risk grid...", flush=True)
grid = pd.read_csv(grid_file)

print("Loading shelter locations...", flush=True)
shelters = pd.read_csv(shelter_file)

print("Creating combined map...", flush=True)

fig, ax = plt.subplots(figsize=(13, 10))

for category, color in [
    ("Lower Risk", "green"),
    ("High Risk", "red")
]:
    subset = grid[grid["risk_category"] == category]
    ax.scatter(
        subset["longitude"],
        subset["latitude"],
        c=color,
        s=9,
        alpha=0.45
    )

for category, color in [
    ("Lower Risk", "blue"),
    ("High Risk", "orange")
]:
    subset = shelters[shelters["risk_category"] == category]
    ax.scatter(
        subset["longitude"],
        subset["latitude"],
        c=color,
        marker="^",
        s=45,
        edgecolors="black",
        linewidths=0.4
    )

legend_items = [
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor="green", markersize=7,
           label="Grid: Lower Risk"),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor="red", markersize=7,
           label="Grid: High Risk"),
    Line2D([0], [0], marker="^", color="w",
           markerfacecolor="blue", markeredgecolor="black",
           markersize=9, label="Shelter: Lower Risk"),
    Line2D([0], [0], marker="^", color="w",
           markerfacecolor="orange", markeredgecolor="black",
           markersize=9, label="Shelter: High Risk")
]

ax.legend(handles=legend_items, loc="best")
ax.set_title("Flood Risk and Potential Shelter Locations - Koshi Basin, Nepal")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.grid(True, linestyle="--", alpha=0.3)

plt.tight_layout()
plt.savefig(output_file, dpi=300)
plt.close()

print("\nCOMBINED MAP CREATED SUCCESSFULLY")
print("Flood grid cells:", len(grid))
print("Potential shelters:", len(shelters))
print("Saved:", output_file)