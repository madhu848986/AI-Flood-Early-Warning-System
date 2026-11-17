
import pandas as pd
from pathlib import Path

file_path = Path("datasets/raw/flood_events/Global_Flood_Records.csv")

if not file_path.exists():
    print("CSV file not found!")
    print("Check the datasets/raw/flood_events folder.")
else:
    data = pd.read_csv(file_path)

    print("FLOOD EVENT DATASET INSPECTION")
    print("=" * 40)

    print("\nTotal records:", len(data))

    print("\nColumn names:")
    print(data.columns.tolist())

    print("\nFirst 5 records:")
    print(data.head().to_string(index=False))

    print("\nMissing values in each column:")
    print(data.isnull().sum().to_string())

    print("\nDataset information:")
    print(data.info())
