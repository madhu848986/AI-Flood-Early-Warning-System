import pandas as pd

df = pd.read_csv(
    "datasets/processed/koshi_event_analysis_dataset.csv"
)

elevation = pd.read_csv(
    "datasets/processed/koshi_elevation_dataset.csv"
)

df = df.merge(
    elevation[["latitude", "longitude", "elevation_m"]],
    on=["latitude", "longitude"],
    how="inner"
)

df["flood_pixel_percentage"] = (
    df["flood_pixels"] / df["valid_pixels"]
) * 100

thresholds = [0, 0.1, 0.5, 1, 2, 5]

print("ALTERNATIVE FLOOD LABEL ANALYSIS")
print("--------------------------------")

for threshold in thresholds:
    df["alternative_label"] = (
        df["flood_pixel_percentage"] > threshold
    ).astype(int)

    positive = df["alternative_label"].sum()
    negative = len(df) - positive

    high_elevation_positive = (
        df[
            (df["elevation_m"] >= 4000) &
            (df["alternative_label"] == 1)
        ].shape[0]
    )

    print(f"\nThreshold: > {threshold}%")
    print(f"Flood-labelled cells: {positive}")
    print(f"Non-flood-labelled cells: {negative}")
    print(
        "High-elevation flood-labelled cells:",
        high_elevation_positive
    )