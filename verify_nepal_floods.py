
import pandas as pd
from pathlib import Path

file_path = Path("datasets/processed/nepal_flood_events.csv")

if not file_path.exists():
    print("Nepal flood dataset not found.")
else:
    data = pd.read_csv(file_path)

    print("NEPAL FLOOD DATASET VERIFICATION")
    print("=" * 40)
    print("Total records:", len(data))

    data["Start Date"] = pd.to_datetime(
        data["Start Date"], errors="coerce"
    )
    data["End Date"] = pd.to_datetime(
        data["End Date"], errors="coerce"
    )

    print("\nDate range:")
    print("Earliest:", data["Start Date"].min())
    print("Latest:", data["End Date"].max())

    print("\nRecords by year:")
    print(data["Start Date"].dt.year.value_counts().sort_index())

    print("\nRecords involving Nepal and India:")
    print(
        data[data["Country"].str.contains("India", case=False, na=False)]
        [["Start Date", "End Date", "Country", "Area (km²)"]]
        .to_string(index=False)
    )

    print("\nMissing values:")
    print(data.isnull().sum().to_string())
