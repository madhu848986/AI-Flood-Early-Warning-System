import pandas as pd

df = pd.read_csv(
    "datasets/processed/koshi_event_analysis_dataset.csv"
)

df["flood_pixel_percentage"] = (
    df["flood_pixels"] / df["valid_pixels"]
) * 100

print("FLOOD PIXEL PERCENTAGE SUMMARY")
print("--------------------------------")

print(
    df.groupby("flood_label")["flood_pixel_percentage"]
    .describe()
    .round(4)
)

print("\nFLOOD LABEL COUNTS AT DIFFERENT THRESHOLDS")
print("------------------------------------------")

thresholds = [0, 0.1, 0.5, 1, 2, 5]

for threshold in thresholds:
    count = (
        df["flood_pixel_percentage"] > threshold
    ).sum()

    print(
        f"Above {threshold}%: {count} cells"
    )

print("\nHIGH-ELEVATION PIXEL PERCENTAGES")

elevation_df = pd.read_csv(
    "datasets/processed/koshi_elevation_dataset.csv"
)

merged = df.merge(
    elevation_df[["latitude", "longitude", "elevation_m"]],
    on=["latitude", "longitude"],
    how="inner"
)

print(
    merged[merged["elevation_m"] >= 4000][
        [
            "latitude",
            "longitude",
            "elevation_m",
            "flood_pixel_percentage"
        ]
    ].to_string(index=False)
)