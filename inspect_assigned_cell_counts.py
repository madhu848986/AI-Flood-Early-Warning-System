import pandas as pd

path = "datasets/processed/modis_flood_by_rainfall_cell.csv"

df = pd.read_csv(path)

print("AGGREGATED CELL COUNT CHECK")
print("=" * 40)

print("Total rainfall cells:", len(df))
print("Cells with valid pixels:",
      (df["valid_pixel_count"] > 0).sum())

print("\nValid pixel count statistics:")
print(df["valid_pixel_count"].describe())

print("\nCells with the most valid pixels:")
print(
    df.nlargest(10, "valid_pixel_count")[
        [
            "latitude",
            "longitude",
            "valid_pixel_count",
            "class_3_count",
            "class_3_proportion",
        ]
    ].to_string(index=False)
)

print("\nCells with zero valid pixels:",
      (df["valid_pixel_count"] == 0).sum())