
import pandas as pd
import matplotlib.pyplot as plt

file_path = "datasets/processed/koshi_rainfall_elevation.csv"
df = pd.read_csv(file_path)

# Use one date to visualize the spatial distribution
date_to_plot = df["date"].min()
day_data = df[df["date"] == date_to_plot]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

rain_plot = axes[0].scatter(
    day_data["longitude"],
    day_data["latitude"],
    c=day_data["precipitation_mm_per_day"],
    s=18
)
axes[0].set_title("Rainfall on " + date_to_plot)
axes[0].set_xlabel("Longitude")
axes[0].set_ylabel("Latitude")
fig.colorbar(rain_plot, ax=axes[0], label="Rainfall (mm/day)")

elev_plot = axes[1].scatter(
    day_data["longitude"],
    day_data["latitude"],
    c=day_data["elevation_m"],
    s=18
)
axes[1].set_title("Elevation Distribution")
axes[1].set_xlabel("Longitude")
axes[1].set_ylabel("Latitude")
fig.colorbar(elev_plot, ax=axes[1], label="Elevation (m)")

plt.tight_layout()

output_path = "datasets/processed/koshi_rainfall_elevation_scatter.png"
plt.savefig(output_path, dpi=150)
plt.close()

print("Plot saved to:", output_path)
