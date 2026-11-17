import pandas as pd
from pathlib import Path

folder = Path("datasets/processed")

files = [
    "koshi_rainfall_accumulation_october_2021.csv",
    "koshi_rainfall_flood_integrated.csv",
    "koshi_event_analysis_dataset.csv",
    "koshi_pre_event_flood_dataset.csv"
]

for name in files:
    path = folder / name

    print("\n" + "=" * 60)
    print(name)

    if not path.exists():
        print("File not found")
        continue

    df = pd.read_csv(path)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        print("\nDate range:")
        print(df["date"].min(), "to", df["date"].max())

        print("\nRecords per date:")
        print(df.groupby("date").size())

    if "flood_observation_available" in df.columns:
        print("\nFlood observation availability:")
        print(df["flood_observation_available"].value_counts(dropna=False))

    if "observed_flood_present" in df.columns:
        print("\nObserved flood labels:")
        print(df["observed_flood_present"].value_counts(dropna=False))

    if "flood_label" in df.columns:
        print("\nFlood label distribution:")
        print(df["flood_label"].value_counts(dropna=False))

    if "rainfall_3day_mm" in df.columns:
        print("\n3-day rainfall missing values:")
        print(df["rainfall_3day_mm"].isna().sum())

    if "rainfall_7day_mm" in df.columns:
        print("\n7-day rainfall missing values:")
        print(df["rainfall_7day_mm"].isna().sum())