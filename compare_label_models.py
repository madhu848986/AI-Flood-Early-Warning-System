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

df = pd.read_csv(
    "datasets/processed/koshi_alternative_label_dataset.csv"
)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude"
]

X = df[features]

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

selected_split = None

for train_idx, test_idx in splitter.split(X, groups=groups):
    selected_split = (train_idx, test_idx)
    break

train_idx, test_idx = selected_split

results = []

for label in ["label_0", "label_1", "label_2", "label_3"]:

    y = df[label]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    if y_train.nunique() < 2 or y_test.nunique() < 2:
        print(f"\nSkipping {label}: only one class in train or test.")
        continue

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42
    )

    model.fit(X.iloc[train_idx], y_train)

    predictions = model.predict(X.iloc[test_idx])
    probabilities = model.predict_proba(X.iloc[test_idx])[:, 1]

    results.append({
        "label": label,
        "positive_cells": int(y.sum()),
        "test_positive_cells": int(y_test.sum()),
        "accuracy": accuracy_score(y_test, predictions),
        "balanced_accuracy": balanced_accuracy_score(
            y_test, predictions
        ),
        "roc_auc": roc_auc_score(y_test, probabilities),
        "precision": precision_score(
            y_test, predictions, zero_division=0
        ),
        "recall": recall_score(
            y_test, predictions, zero_division=0
        ),
        "f1_score": f1_score(
            y_test, predictions, zero_division=0
        )
    })

result_df = pd.DataFrame(results)

print("\nRANDOM FOREST LABEL COMPARISON")
print("--------------------------------")

print(result_df.round(4).to_string(index=False))

result_df.to_csv(
    "datasets/processed/label_model_comparison.csv",
    index=False
)

print("\nSaved: datasets/processed/label_model_comparison.csv")