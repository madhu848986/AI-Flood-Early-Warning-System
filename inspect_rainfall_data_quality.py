import pandas as pd

INPUT_CSV = (
    "datasets/processed/koshi_event_analysis_dataset.csv"
)

df = pd.read_csv(INPUT_CSV)

rainfall_columns = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm"
]

print("RAINFALL DATA QUALITY")
print("---------------------")

for column in rainfall_columns:

    print("\n", column)
    print("-" * 35)

    print(df[column].describe().round(3))

    print(
        "Zero values:",
        (df[column] == 0).sum()
    )

    print(
        "Positive values:",
        (df[column] > 0).sum()
    )

    print(
        "Missing values:",
        df[column].isna().sum()
    )

print("\nRAINFALL BY FLOOD LABEL")
print("-----------------------")

print(
    df.groupby("flood_label")[rainfall_columns]
    .agg(["mean", "median", "max"])
    .round(3)
)

print("\nSaved input inspected:", INPUT_CSV)