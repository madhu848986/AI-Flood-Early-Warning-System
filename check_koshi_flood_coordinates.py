import pandas as pd

file_path = (
    "datasets/processed/"
    "koshi_nasa_flood_pixels.csv"
)

df = pd.read_csv(file_path)

print("NASA FLOOD COORDINATE CHECK")
print("=" * 40)

print("Total rows:", len(df))

print("\nLatitude range:")
print("Minimum:", df["latitude"].min())
print("Maximum:", df["latitude"].max())

print("\nLongitude range:")
print("Minimum:", df["longitude"].min())
print("Maximum:", df["longitude"].max())

print("\nMissing coordinates:")
print(df[["latitude", "longitude"]].isna().sum())

print("\nFlood class counts:")
print(df["flood_class"].value_counts().sort_index())