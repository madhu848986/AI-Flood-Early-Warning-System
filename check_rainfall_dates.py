import pandas as pd

file_path = (
    "datasets/processed/"
    "koshi_rainfall_elevation.csv"
)

df = pd.read_csv(file_path)

df["date"] = pd.to_datetime(df["date"], errors="coerce")

print("RAINFALL DATE CHECK")
print("=" * 40)
print("Total rows:", len(df))
print("First date:", df["date"].min())
print("Last date:", df["date"].max())
print("Missing dates:", df["date"].isna().sum())
print("Unique dates:", df["date"].nunique())