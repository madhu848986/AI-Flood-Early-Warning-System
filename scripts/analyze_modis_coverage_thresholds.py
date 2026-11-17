
import pandas as pd

file_path = (
    "datasets/processed/"
    "modis_flood_by_rainfall_cell_cs_quality.csv"
)

df = pd.read_csv(file_path)

df["coverage_pct"] = (
    df["classified_pixel_count"] /
    df["total_pixel_count"] * 100
)

df["flood_pct"] = (
    df["class_3_count"] /
    df["classified_pixel_count"].replace(0, pd.NA) * 100
)

print("\nMODIS COVERAGE SENSITIVITY ANALYSIS")
print("=" * 85)

print("Total grid cells:", len(df))
print("Cells with classified observations:",
      (df["classified_pixel_count"] > 0).sum())

print("\nCOVERAGE THRESHOLD COMPARISON")
print("-" * 85)

for threshold in [0, 1, 5, 10, 25, 50, 75, 90]:
    selected = df[df["coverage_pct"] >= threshold]

    positive = selected[selected["class_3_count"] > 0]
    negative = selected[
        (selected["class_3_count"] == 0) &
        (selected["classified_pixel_count"] > 0)
    ]

    print(
        f"Coverage >= {threshold:2}% | "
        f"Cells: {len(selected):4} | "
        f"Positive: {len(positive):3} | "
        f"Negative: {len(negative):3} | "
        f"Unknown: {len(selected) - len(positive) - len(negative):3}"
    )

print("\nHIGH-ALTITUDE POSITIVE CELL RETENTION")
print("-" * 85)

model_file = (
    "datasets/processed/"
    "koshi_oct13_model_features_cs_v3_spatial_folds.csv"
)

model = pd.read_csv(model_file)

high = model[
    (model["observed_flood_present"] == 1) &
    (model["elevation_mean_m"] >= 4000)
]

high = high.merge(
    df[["latitude", "longitude", "coverage_pct"]],
    on=["latitude", "longitude"],
    how="left"
)

for threshold in [1, 5, 10, 25, 50, 75, 90]:
    retained = high[high["coverage_pct"] >= threshold]
    print(
        f"Coverage >= {threshold:2}%: "
        f"{len(retained)} of {len(high)} high-altitude positives retained"
    )

print("\nANALYSIS COMPLETED")
