import pandas as pd

rainfall_path = (
    "datasets/processed/koshi_rainfall_october_13_14_2021.csv"
)

flood_path = (
    "datasets/processed/koshi_modis_flood_cell_summary.csv"
)

rainfall = pd.read_csv(rainfall_path)
flood = pd.read_csv(flood_path)

print("RAINFALL DATA")
print("=" * 40)
print("Rows:", len(rainfall))
print("Columns:", rainfall.columns.tolist())
print("Dates:", sorted(rainfall["date"].unique()))
print("Latitude range:", rainfall["latitude"].min(),
      "to", rainfall["latitude"].max())
print("Longitude range:", rainfall["longitude"].min(),
      "to", rainfall["longitude"].max())

print("\nFLOOD SUMMARY")
print("=" * 40)
print("Rows:", len(flood))
print("Columns:", flood.columns.tolist())
print("Latitude range:", flood["latitude"].min(),
      "to", flood["latitude"].max())
print("Longitude range:", flood["longitude"].min(),
      "to", flood["longitude"].max())

print("\nFLOOD OBSERVATION COUNTS")
print("=" * 40)
print("Cells with valid observations:", len(flood))
print("Cells with flood pixels:",
      (flood["flood_pixels"] > 0).sum())
print("Cells with recurring-flood pixels:",
      (flood["recurring_flood_pixels"] > 0).sum())