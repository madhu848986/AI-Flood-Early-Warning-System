import pandas as pd
from pathlib import Path

folder = Path("datasets/processed")

# 1. Nepal historical flood events
events = pd.read_csv(folder / "nepal_flood_events.csv")

print("\nNEPAL FLOOD EVENTS")
print("=" * 60)

events["Start Date"] = pd.to_datetime(
    events["Start Date"], errors="coerce"
)

events["End Date"] = pd.to_datetime(
    events["End Date"], errors="coerce"
)

print(events[
    ["Start Date", "End Date", "Country",
     "Area (km²)", "Main Cause", "Severity"]
].sort_values("Start Date").to_string(index=False))

print("\nEvents during October 2021:")
print(events[
    (events["Start Date"] <= "2021-10-31") &
    (events["End Date"] >= "2021-10-01")
][["Start Date", "End Date", "Country", "Main Cause"]].to_string(index=False))


# 2. NASA flood pixel classes
path = folder / "koshi_nasa_flood_pixels.csv"

print("\nNASA FLOOD PIXEL ANALYSIS")
print("=" * 60)

df = pd.read_csv(path)

print("Shape:", df.shape)

print("\nFlood class distribution:")
print(df["flood_class"].value_counts(dropna=False))

print("\nCoordinate ranges:")
print("Latitude:", df["latitude"].min(), "to", df["latitude"].max())
print("Longitude:", df["longitude"].min(), "to", df["longitude"].max())

print("\nUnique flood classes:")
print(sorted(df["flood_class"].dropna().unique().tolist()))