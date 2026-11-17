import pandas as pd

df = pd.read_csv(
    "datasets/processed/koshi_ml_dataset_with_elevation.csv"
)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "elevation_m",
    "latitude",
    "longitude"
]

print("CORRELATION WITH FLOOD LABEL")
print("----------------------------")

correlation = df[features + ["flood_label"]].corr()

print(
    correlation["flood_label"]
    .sort_values(ascending=False)
    .round(4)
)

print("\nAVERAGE VALUES BY FLOOD LABEL")
print("-----------------------------")

print(
    df.groupby("flood_label")[features]
    .mean()
    .round(4)
)

print("\nRAINFALL SUMMARY")
print("----------------")

print(
    df[features[:3]]
    .describe()
    .round(4)
)