import pandas as pd

event_df = pd.read_csv(
    "datasets/processed/koshi_event_analysis_dataset.csv"
)

elevation_df = pd.read_csv(
    "datasets/processed/koshi_elevation_dataset.csv"
)

print("EVENT DATASET COLUMNS:")
print(event_df.columns.tolist())

print("\nELEVATION DATASET COLUMNS:")
print(elevation_df.columns.tolist())

df = pd.merge(
    event_df,
    elevation_df,
    on=["latitude", "longitude"],
    how="inner"
)

print("\nMERGED DATASET COLUMNS:")
print(df.columns.tolist())

print("\nMERGED RECORD COUNT:", len(df))