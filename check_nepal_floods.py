
import pandas as pd
from pathlib import Path

file_path = Path("datasets/raw/flood_events/Global_Flood_Records.csv")

data = pd.read_csv(file_path)

data["Country"] = data["Country"].astype(str).str.strip()

nepal_data = data[
    data["Country"].str.contains("Nepal", case=False, na=False)
].copy()

print("TOTAL GLOBAL FLOOD RECORDS:", len(data))
print("NEPAL FLOOD RECORDS:", len(nepal_data))

if nepal_data.empty:
    print("\nNo records for Nepal were found.")
else:
    print("\nNepal flood records:")
    print(
        nepal_data[
            ["Start Date", "End Date", "Country",
             "Area (km²)", "Main Cause", "Fatalities",
             "Displaced", "Severity"]
        ].to_string(index=False)
    )

    output_path = Path(
        "datasets/processed/nepal_flood_events.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nepal_data.to_csv(output_path, index=False)

    print("\nSaved Nepal records to:", output_path)
