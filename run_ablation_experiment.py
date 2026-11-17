import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    roc_auc_score,
    recall_score,
    f1_score
)

INPUT_FILE = "datasets/processed/koshi_ml_dataset_with_elevation.csv"

df = pd.read_csv(INPUT_FILE)

feature_groups = {
    "Rainfall Only": [
        "daily_rainfall_mm",
        "rainfall_3day_mm",
        "rainfall_7day_mm"
    ],
    "Rainfall + Elevation": [
        "daily_rainfall_mm",
        "rainfall_3day_mm",
        "rainfall_7day_mm",
        "elevation_m"
    ],
    "Rainfall + Elevation + Coordinates": [
        "daily_rainfall_mm",
        "rainfall_3day_mm",
        "rainfall_7day_mm",
        "elevation_m",
        "latitude",
        "longitude"
    ]
}

y = df["flood_label"]

df["spatial_group"] = (
    (df["latitude"] // 0.5).astype(int).astype(str)
    + "_"
    + (df["longitude"] // 0.5).astype(int).astype(str)
)

groups = df["spatial_group"]

splitter = GroupShuffleSplit(
    n_splits=10,
    test_size=0.25,
    random_state=42
)

for train_idx, test_idx in splitter.split(df, y, groups):
    if (
        y.iloc[train_idx].nunique() == 2
        and y.iloc[test_idx].nunique() == 2
    ):
        break

y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

results = []

for name, features in feature_groups.items():

    X_train = df.iloc[train_idx][features]
    X_test = df.iloc[test_idx][features]

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
        "Feature Group": name,
        "Accuracy": accuracy_score(y_test, predictions),
        "Balanced Accuracy": balanced_accuracy_score(
            y_test, predictions
        ),
        "ROC-AUC": roc_auc_score(y_test, probabilities),
        "Flood Recall": recall_score(
            y_test, predictions, zero_division=0
        ),
        "Flood F1-score": f1_score(
            y_test, predictions, zero_division=0
        )
    })

comparison = pd.DataFrame(results)

output_file = "datasets/processed/ablation_comparison.csv"
comparison.to_csv(output_file, index=False)

print("ABLATION EXPERIMENT RESULTS")
print("---------------------------")
print(comparison.to_string(index=False))

print("\nSaved at:", output_file)