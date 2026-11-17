import pandas as pd

event_df = pd.read_csv(
    "datasets/processed/koshi_event_analysis_dataset.csv"
)

elevation_df = pd.read_csv(
    "datasets/processed/koshi_elevation_dataset.csv"
)

df = pd.merge(
    event_df[[
        "latitude",
        "longitude",
        "flood_label",
        "flood_pixels",
        "recurring_flood_pixels",
        "no_water_pixels",
        "flood_pixel_ratio",
        "recurring_or_flood_ratio"
    ]],
    elevation_df[[
        "latitude",
        "longitude",
        "elevation_m"
    ]],
    on=["latitude", "longitude"],
    how="inner"
)

high_flood = df[
    (df["flood_label"] == 1) &
    (df["elevation_m"] >= 4000)
]

print("HIGH-ELEVATION FLOOD-LABELLED CELLS")
print("-----------------------------------")
print("Total cells:", len(high_flood))

columns = [
    "latitude",
    "longitude",
    "elevation_m",
    "flood_pixels",
    "recurring_flood_pixels",
    "no_water_pixels",
    "flood_pixel_ratio",
    "recurring_or_flood_ratio"
]

print(high_flood[columns].to_string(index=False))