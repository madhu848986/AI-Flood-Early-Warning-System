import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

input_file = "datasets/processed/koshi_shelter_recommendations.csv"
output_file = "datasets/processed/koshi_shelter_distribution_map.png"

print("Loading shelter data...", flush=True)

data = pd.read_csv(input_file)

gdf = gpd.GeoDataFrame(
    data,
    geometry=gpd.points_from_xy(data["longitude"], data["latitude"]),
    crs="EPSG:4326"
)

print("Creating shelter distribution map...", flush=True)

fig, ax = plt.subplots(figsize=(12, 9))

for category, color, label in [
    ("Lower Risk", "green", "Lower Preliminary Risk"),
    ("High Risk", "red", "Higher Preliminary Risk")
]:
    subset = gdf[gdf["risk_category"] == category]
    subset.plot(
        ax=ax,
        color=color,
        markersize=12,
        alpha=0.7,
        label=label
    )

ax.set_title("Potential Shelter Distribution - Koshi Basin, Nepal")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.3)

plt.tight_layout()
plt.savefig(output_file, dpi=300)
plt.close()

print("\nMAP CREATED SUCCESSFULLY")
print("Total shelters:", len(gdf))
print("Lower Risk:", (gdf["risk_category"] == "Lower Risk").sum())
print("High Risk:", (gdf["risk_category"] == "High Risk").sum())
print("Saved:", output_file)