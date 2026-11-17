import pandas as pd

rainfall_path = (
    "datasets/processed/"
    "koshi_rainfall_october_13_14_2021.csv"
)

flood_path = (
    "datasets/processed/"
    "koshi_nasa_flood_pixels.csv"
)

rainfall = pd.read_csv(rainfall_path)
flood = pd.read_csv(flood_path)

print("RAINFALL AND FLOOD DATA CHECK")
print("=" * 45)

print("\nRainfall dates:")
print(sorted(rainfall["date"].unique()))

print("\nRainfall coordinate ranges:")
print("Latitude:", rainfall["latitude"].min(),
      "to", rainfall["latitude"].max())
print("Longitude:", rainfall["longitude"].min(),
      "to", rainfall["longitude"].max())

print("\nFlood coordinate ranges:")
print("Latitude:", flood["latitude"].min(),
      "to", flood["latitude"].max())
print("Longitude:", flood["longitude"].min(),
      "to", flood["longitude"].max())

print("\nRainfall records:", len(rainfall))
print("Flood pixels:", len(flood))

print("\nFlood classes:")
print(flood["flood_class"].value_counts().sort_index())

print("\nCheck completed.")