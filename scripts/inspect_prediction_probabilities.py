
import pandas as pd

input_file = (
    "datasets/processed/"
    "spatial_logistic_regression_predictions.csv"
)

df = pd.read_csv(input_file)

print("\nPREDICTION PROBABILITY ANALYSIS")
print("=" * 60)

print("\nOVERALL PROBABILITY STATISTICS")
print(df["predicted_probability"].describe())

print("\nPROBABILITY DISTRIBUTION BY ACTUAL CLASS")

summary = df.groupby("actual")["predicted_probability"].agg(
    ["count", "mean", "std", "min", "median", "max"]
)

print(summary.round(4).to_string())

print("\nPROBABILITY DISTRIBUTION BY FOLD")

fold_summary = df.groupby(["fold", "actual"])[
    "predicted_probability"
].agg(["count", "mean", "std", "median"])

print(fold_summary.round(4).to_string())

print("\nANALYSIS COMPLETED")
