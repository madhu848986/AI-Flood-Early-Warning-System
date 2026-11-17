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

elevation = pd.read_csv(
    "datasets/processed/koshi_elevation_dataset.csv"
)

df = df.merge(
    elevation[["latitude", "longitude", "elevation_m"]],
    on=["latitude", "longitude"],
    how="inner"
)

feature_sets = {
    "Rainfall only": [
        "daily_rainfall_mm",
        "rainfall_3day_mm",
        "rainfall_7day_mm"
    ],
    "Rainfall + coordinates": [
        "daily_rainfall_mm",
        "rainfall_3day_mm",
        "rainfall_7day_mm",
        "latitude",
        "longitude"
    ],
    "Rainfall + coordinates + elevation": [
        "daily_rainfall_mm",
        "rainfall_3day_mm",
        "rainfall_7day_mm",
        "latitude",
        "longitude",
        "elevation_m"
    ]
}

y = df["label_2"]

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

train_idx, test_idx = next(
    splitter.split(df, y, groups)
)

results = []

for name, features in feature_sets.items():

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42
    )

    model.fit(
        df.iloc[train_idx][features],
        y.iloc[train_idx]
    )

    predictions = model.predict(
        df.iloc[test_idx][features]
    )

    probabilities = model.predict_proba(
        df.iloc[test_idx][features]
    )[:, 1]

    results.append({
        "feature_set": name,
        "accuracy": accuracy_score(
            y.iloc[test_idx], predictions
        ),
        "balanced_accuracy": balanced_accuracy_score(
            y.iloc[test_idx], predictions
        ),
        "roc_auc": roc_auc_score(
            y.iloc[test_idx], probabilities
        ),
        "precision": precision_score(
            y.iloc[test_idx], predictions,
            zero_division=0
        ),
        "recall": recall_score(
            y.iloc[test_idx], predictions,
            zero_division=0
        ),
        "f1_score": f1_score(
            y.iloc[test_idx], predictions,
            zero_division=0
        )
    })

result_df = pd.DataFrame(results)

print("\nSPATIAL FEATURE SET COMPARISON")
print("--------------------------------")
print(result_df.round(4).to_string(index=False))

result_df.to_csv(
    "datasets/processed/spatial_feature_comparison.csv",
    index=False
)

print("\nSaved: datasets/processed/spatial_feature_comparison.csv")