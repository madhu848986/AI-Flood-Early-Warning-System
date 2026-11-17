import pandas as pd
from pathlib import Path

files = [
    Path("datasets/raw/flood_events/Global_Flood_Records.csv"),
    Path("datasets/processed/koshi_rainfall_september_2020.csv"),
    Path("datasets/processed/nepal_flood_events.csv"),
    Path("datasets/processed/koshi_nasa_flood_pixels.csv")
]

for file in files:
    print("\n" + "=" * 65)
    print("FILE:", file)
    print("=" * 65)

    if not file.exists():
        print("NOT FOUND")
        continue

    df = pd.read_csv(file)

    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("\nFirst 3 records:")
    print(df.head(3).to_string(index=False))

    date_columns = [
        c for c in df.columns
        if any(word in c.lower() for word in ["date", "time", "start", "end"])
    ]

    for column in date_columns:
        print("\nDate information:", column)
        print(df[column].head(5).to_list())