import pandas as pd

df = pd.read_csv(
    "datasets/processed/koshi_event_analysis_dataset.csv"
)

df["flood_pixel_percentage"] = (
    df["flood_pixels"] / df["valid_pixels"]
) * 100

df["label_0"] = (
    df["flood_pixel_percentage"] > 0
).astype(int)

df["label_1"] = (
    df["flood_pixel_percentage"] > 1
).astype(int)

df["label_2"] = (
    df["flood_pixel_percentage"] > 2
).astype(int)

df["label_3"] = (
    df["flood_pixel_percentage"] > 5
).astype(int)

output = "datasets/processed/koshi_alternative_label_dataset.csv"

df.to_csv(output, index=False)

print("Alternative label dataset created.")
print("Records:", len(df))

for column in ["label_0", "label_1", "label_2", "label_3"]:
    print(f"\n{column}")
    print(df[column].value_counts().sort_index())

print("\nSaved:", output)