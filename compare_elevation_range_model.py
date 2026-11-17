import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score
)

INPUT_CSV = (
    "datasets/processed/koshi_ml_dataset_with_terrain_range.csv"
)

df = pd.read_csv(INPUT_CSV)

groups = (
    (df["latitude"] // 0.5).astype(str)
    + "_"
    + (df["longitude"] // 0.5).astype(str)
)

splitter = GroupShuffleSplit(
    n_splits=10,
    test_size=0.25,
    random_state=42
)

train_index, test_index = next(
    splitter.split(df, df["flood_label"], groups)
)

feature_sets = {
    "Zonal mean elevation": [
        "daily_rainfall_mm",
        "rainfall_3day_mm",
        "rainfall_7day_mm",
        "latitude",
        "longitude",
        "elevation_mean_m"
    ],
    "Zonal mean + elevation range": [
        "daily_rainfall_mm",
        "rainfall_3day_mm",
        "rainfall_7day_mm",
        "latitude",
        "longitude",
        "elevation_mean_m",
        "elevation_range_m"
    ]
}

results = []

for name, features in feature_sets.items():

    X = df[features]
    y = df["flood_label"]

    X_train = X.iloc[train_index]
    X_test = X.iloc[test_index]

    y_train = y.iloc[train_index]
    y_test = y.iloc[test_index]

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    results.append({
        "model": name,
        "accuracy": accuracy_score(y_test, predictions),
        "balanced_accuracy": balanced_accuracy_score(
            y_test, predictions
        ),
        "roc_auc": roc_auc_score(y_test, probabilities),
        "flood_precision": precision_score(
            y_test, predictions, zero_division=0
        ),
        "flood_recall": recall_score(
            y_test, predictions, zero_division=0
        ),
        "flood_f1": f1_score(
            y_test, predictions, zero_division=0
        )
    })

result_df = pd.DataFrame(results)

print("\nELEVATION RANGE MODEL COMPARISON")
print("--------------------------------")
print(result_df.round(4).to_string(index=False))

OUTPUT_CSV = (
    "datasets/processed/elevation_range_model_comparison.csv"
)

result_df.to_csv(OUTPUT_CSV, index=False)

print("\nSaved:", OUTPUT_CSV)