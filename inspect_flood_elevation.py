import pandas as pd

df = pd.read_csv(
    "datasets/processed/koshi_ml_dataset_with_elevation.csv"
)

print("ELEVATION SUMMARY BY FLOOD LABEL")
print("--------------------------------")

print(
    df.groupby("flood_label")["elevation_m"]
    .describe()
    .round(2)
)

print("\nFLOOD LABEL COUNTS BY ELEVATION RANGE")
print("------------------------------------")

df["elevation_band"] = pd.cut(
    df["elevation_m"],
    bins=[0, 100, 500, 1000, 2000, 4000, 9000],
    labels=[
        "0-100 m",
        "100-500 m",
        "500-1000 m",
        "1000-2000 m",
        "2000-4000 m",
        "4000+ m"
    ]
)

print(
    pd.crosstab(
        df["elevation_band"],
        df["flood_label"],
        margins=True
    )
)

print("\nFLOOD-LABELLED CELL LOCATIONS")
print("-----------------------------")

print(
    df[df["flood_label"] == 1][
        ["latitude", "longitude", "elevation_m"]
    ].head(20).to_string(index=False)
)