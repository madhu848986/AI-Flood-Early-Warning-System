import pandas as pd
import numpy as np

input_path = "datasets/processed/koshi_nasa_flood_pixels.csv"
output_path = "datasets/processed/koshi_modis_flood_cell_summary.csv"

flood = pd.read_csv(input_path)

cell_step = 0.1

# Assign pixels to rainfall-grid cells
flood["cell_row"] = np.floor(
    (flood["latitude"] - 25.0) / cell_step
).astype(int)

flood["cell_col"] = np.floor(
    (flood["longitude"] - 85.0) / cell_step
).astype(int)

# Exclude pixels with insufficient data
valid = flood[flood["flood_class"] != 255].copy()

# Count each observed flood class per cell
summary = (
    valid.groupby(["cell_row", "cell_col", "flood_class"])
    .size()
    .unstack(fill_value=0)
)

summary = summary.reindex(columns=[0, 1, 2, 3], fill_value=0)
summary.columns = [
    "no_water_pixels",
    "reference_water_pixels",
    "recurring_flood_pixels",
    "flood_pixels",
]

summary["valid_pixels"] = summary.sum(axis=1)

summary["flood_pixel_ratio"] = np.where(
    summary["valid_pixels"] > 0,
    summary["flood_pixels"] / summary["valid_pixels"],
    np.nan,
)

summary["recurring_or_flood_ratio"] = np.where(
    summary["valid_pixels"] > 0,
    (
        summary["recurring_flood_pixels"]
        + summary["flood_pixels"]
    ) / summary["valid_pixels"],
    np.nan,
)

summary = summary.reset_index()

# Convert cell indices back to rainfall-grid center coordinates
summary["latitude"] = 25.05 + summary["cell_row"] * cell_step
summary["longitude"] = 85.05 + summary["cell_col"] * cell_step

summary.to_csv(output_path, index=False)

print("FLOOD CELL SUMMARY")
print("=" * 40)
print("Valid pixels:", len(valid))
print("Cells with valid observations:", len(summary))
print("Output:", output_path)
print("\nFlood class totals:")
print(summary[
    [
        "no_water_pixels",
        "reference_water_pixels",
        "recurring_flood_pixels",
        "flood_pixels",
    ]
].sum())

print("\nSample rows:")
print(summary.head())