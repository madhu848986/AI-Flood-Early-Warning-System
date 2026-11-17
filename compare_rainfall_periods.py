import pandas as pd

historical_path = (
    "datasets/processed/koshi_rainfall_september_2020.csv"
)

october_path = (
    "datasets/processed/koshi_rainfall_october_13_14_2021.csv"
)

historical = pd.read_csv(historical_path)
october = pd.read_csv(october_path)

print("HISTORICAL RAINFALL")
print("=" * 40)
print("Date range:", historical["date"].min(),
      "to", historical["date"].max())
print("Rows:", len(historical))
print("Mean rainfall:",
      historical["precipitation_mm_per_day"].mean())
print("Maximum rainfall:",
      historical["precipitation_mm_per_day"].max())

print("\nOCTOBER 2021 RAINFALL")
print("=" * 40)
print("Date range:", october["date"].min(),
      "to", october["date"].max())

print(
    october.groupby("date")["precipitation_mm_per_day"]
    .agg(["mean", "max", "median"])
)

print("\nHistorical and October grid overlap")
print("=" * 40)

historical_cells = set(zip(
    historical["latitude"].round(6),
    historical["longitude"].round(6)
))

october_cells = set(zip(
    october["latitude"].round(6),
    october["longitude"].round(6)
))

print("Historical unique cells:", len(historical_cells))
print("October unique cells:", len(october_cells))
print("Matching cells:", len(historical_cells & october_cells))