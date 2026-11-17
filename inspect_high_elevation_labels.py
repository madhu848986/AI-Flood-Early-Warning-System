import pandas as pd

df = pd.read_csv(
    "datasets/processed/koshi_event_analysis_dataset.csv"
)

elevation = pd.read_csv(
    "datasets/processed/koshi_elevation_dataset.csv"
)

merged = df.merge(
    elevation[["latitude", "longitude", "elevation_m"]],
    on=["latitude", "longitude"],
    how="inner"
)

merged["flood_pixel_percentage"] = (
    merged["flood_pixels"] / merged["valid_pixels"]
) * 100

high = merged[merged["elevation_m"] >= 4000].copy()

high = high.sort_values(
    "flood_pixel_percentage",
    ascending=False
)

columns = [
    "latitude",
    "longitude",
    "elevation_m",
    "valid_pixels",
    "flood_pixels",
    "recurring_flood_pixels",
    "reference_water_pixels",
    "no_water_pixels",
    "flood_pixel_percentage"
]

print("HIGH-ELEVATION MODIS LABEL INSPECTION")
print("-------------------------------------")
print("Total high-elevation cells:", len(high))

print(
    high[columns].to_string(index=False)
)