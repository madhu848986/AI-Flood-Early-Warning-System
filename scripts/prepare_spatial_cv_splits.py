
import os
import pandas as pd

input_file = (
    "datasets/processed/"
    "koshi_oct13_model_features_cs_v3_spatial_folds.csv"
)

output_dir = "datasets/processed/spatial_cv_folds"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_file)

target = "observed_flood_present"
fold_column = "spatial_fold"

feature_columns = [
    "precipitation_mm_per_day",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "elevation_mean_m",
    "elevation_min_m",
    "elevation_max_m",
    "elevation_median_m",
    "elevation_range_m"
]

required_columns = feature_columns + [target, fold_column]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

if df[required_columns].isnull().any().any():
    raise ValueError("Missing values found in model data.")

if df[fold_column].nunique() != 5:
    raise ValueError("Expected exactly five spatial folds.")

print("SPATIAL CROSS-VALIDATION DATA PREPARATION")
print("=" * 50)

for fold in range(1, 6):
    train = df[df[fold_column] != fold].copy()
    test = df[df[fold_column] == fold].copy()

    train_file = os.path.join(
        output_dir, f"fold_{fold}_train.csv"
    )
    test_file = os.path.join(
        output_dir, f"fold_{fold}_test.csv"
    )

    train.to_csv(train_file, index=False)
    test.to_csv(test_file, index=False)

    print(f"\nFold {fold}")
    print("Training records:", len(train))
    print("Testing records:", len(test))
    print("Training classes:")
    print(train[target].value_counts().to_dict())
    print("Testing classes:")
    print(test[target].value_counts().to_dict())

    if train[target].nunique() != 2 or test[target].nunique() != 2:
        raise ValueError(f"Fold {fold} does not contain both classes.")

print("\nAll five train-test splits created successfully.")
print("Output folder:", output_dir)
