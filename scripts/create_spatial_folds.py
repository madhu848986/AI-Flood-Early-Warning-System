
import pandas as pd

input_file = "datasets/processed/koshi_oct13_model_features_cs_v2.csv"
df = pd.read_csv(input_file)

df["lat_block"] = (df["latitude"] // 0.5).astype(int)
df["lon_block"] = (df["longitude"] // 0.5).astype(int)

groups = (
    df.groupby(["lat_block", "lon_block"])["observed_flood_present"]
    .agg(["count", "sum"])
    .reset_index()
)

groups["positive"] = groups["sum"].astype(int)
groups["negative"] = groups["count"] - groups["positive"]

groups = groups.sort_values(
    ["positive", "negative"],
    ascending=False
).reset_index(drop=True)

folds = [
    {"positive": 0, "negative": 0, "blocks": []}
    for _ in range(5)
]

target_pos = groups["positive"].sum() / 5
target_neg = groups["negative"].sum() / 5

for _, row in groups.iterrows():
    scores = []

    for fold in folds:
        old_score = (
            (fold["positive"] - target_pos) ** 2
            + (fold["negative"] - target_neg) ** 2
        )

        new_pos = fold["positive"] + row["positive"]
        new_neg = fold["negative"] + row["negative"]

        new_score = (
            (new_pos - target_pos) ** 2
            + (new_neg - target_neg) ** 2
        )

        scores.append(new_score - old_score)

    best_fold = min(
        range(5),
        key=lambda i: (
            scores[i],
            len(folds[i]["blocks"])
        )
    )

    folds[best_fold]["positive"] += int(row["positive"])
    folds[best_fold]["negative"] += int(row["negative"])
    folds[best_fold]["blocks"].append(
        (int(row["lat_block"]), int(row["lon_block"]))
    )

results = []

for i, fold in enumerate(folds):
    results.append({
        "fold": i + 1,
        "blocks": len(fold["blocks"]),
        "positive": fold["positive"],
        "negative": fold["negative"],
        "total": fold["positive"] + fold["negative"]
    })

result_df = pd.DataFrame(results)

print("\nFIVE SPATIAL FOLDS")
print(result_df.to_string(index=False))

print("\nTOTAL VALIDATION")
print("Blocks:", len(groups))
print("Records:", result_df["total"].sum())
print("Positive:", result_df["positive"].sum())
print("Negative:", result_df["negative"].sum())

print("\nFOLD VALIDATION")
print("All folds populated:", (result_df["blocks"] > 0).all())
print("All folds contain both classes:",
      ((result_df["positive"] > 0) &
       (result_df["negative"] > 0)).all())

block_to_fold = {}

for i, fold in enumerate(folds):
    for lat_block, lon_block in fold["blocks"]:
        block_to_fold[(lat_block, lon_block)] = i + 1

df["spatial_fold"] = df.apply(
    lambda row: block_to_fold[
        (row["lat_block"], row["lon_block"])
    ],
    axis=1
)

output_file = "datasets/processed/koshi_oct13_model_features_cs_v3_spatial_folds.csv"
df.to_csv(output_file, index=False)

print("\nSaved spatial fold dataset:", output_file)
print("\nRecords per fold:")
print(df["spatial_fold"].value_counts().sort_index())