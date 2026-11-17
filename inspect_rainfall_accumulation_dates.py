import pandas as pd

INPUT_CSV = (
    "datasets/processed/koshi_rainfall_accumulation_october_2021.csv"
)

df = pd.read_csv(INPUT_CSV)

print("RAINFALL DATASET DETAILS")
print("------------------------")

print("Total records:", len(df))
print("\nColumns:")
print(df.columns.tolist())

print("\nDate range:")
print("Start:", df["date"].min())
print("End:", df["date"].max())

print("\nUnique dates:")
print(sorted(df["date"].unique()))

print("\nRecords per date:")
print(df.groupby("date").size())

print("\nRainfall summary by date:")

print(
    df.groupby("date")["daily_rainfall_mm"]
    .agg(["count", "mean", "median", "max"])
    .round(3)
)

print("\nSaved input inspected:", INPUT_CSV)