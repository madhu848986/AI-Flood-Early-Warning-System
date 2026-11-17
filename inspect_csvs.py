import pandas as pd
from pathlib import Path

names = [
    "koshi_rainfall_accumulation_october_2021.csv",
    "koshi_rainfall_flood_integrated.csv",
    "koshi_event_analysis_dataset.csv",
    "koshi_pre_event_flood_dataset.csv",
    "koshi_all_grid_flood_predictions.csv"
]

folder = Path("datasets/processed")

for name in names:
    file_path = folder / name

    print("\n---", name, "---")

    if not file_path.exists():
        print("NOT FOUND")
        continue

    df = pd.read_csv(file_path)

    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("\nFirst 2 rows:")
    print(df.head(2).to_string(index=False))