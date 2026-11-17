import pandas as pd
from pathlib import Path

flood_path = Path(
    "datasets/processed/koshi_nasa_flood_pixels.csv"
)

output_path = Path(
    "datasets/processed/modis_flood_class_check.csv"
)

if not flood_path.exists():
    raise FileNotFoundError(f"File not found: {flood_path}")

counts = {}

for chunk in pd.read_csv(flood_path, chunksize=100_000):
    values = chunk["flood_class"].value_counts()

    for flood_class, count in values.items():
        counts[int(flood_class)] = (
            counts.get(int(flood_class), 0) + int(count)
        )

result = pd.DataFrame(
    [
        {"flood_class": flood_class, "pixel_count": count}
        for flood_class, count in sorted(counts.items())
    ]
)

result.to_csv(output_path, index=False)

print("MODIS FLOOD CLASS CHECK")
print("=" * 40)
print(result.to_string(index=False))
print("\nTotal pixels:", result["pixel_count"].sum())
print("Saved to:", output_path)