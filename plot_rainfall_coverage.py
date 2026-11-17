import pandas as pd
import matplotlib.pyplot as plt

path = "datasets/processed/koshi_rainfall_october_13_14_2021.csv"
df = pd.read_csv(path)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

for ax, date in zip(axes, ["2021-10-13", "2021-10-14"]):
    day = df[df["date"] == date]

    scatter = ax.scatter(
        day["longitude"],
        day["latitude"],
        c=day["precipitation_mm_per_day"],
        s=12,
        marker="s"
    )

    # Approximate bounds of the MODIS crop
    ax.axvline(85.0, linestyle="--")
    ax.axvline(88.5, linestyle="--")
    ax.axhline(26.0, linestyle="--")
    ax.axhline(28.5, linestyle="--")

    ax.set_title("Rainfall on " + date)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    fig.colorbar(scatter, ax=ax, label="Rainfall (mm/day)")

plt.tight_layout()
plt.savefig(
    "datasets/processed/rainfall_coverage_map.png",
    dpi=300
)
plt.close()

print("Saved: datasets/processed/rainfall_coverage_map.png")