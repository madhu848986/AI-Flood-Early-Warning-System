import pandas as pd
import joblib

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
    "datasets/processed/koshi_elevation_zonal_dataset.csv"
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

results = []

for elevation_feature in [
    "elevation_m",
    "elevation_mean_m",
    "elevation_median_m"
]:

    if elevation_feature == "elevation_m":
        source = pd.read_csv(
            "datasets/processed/koshi_elevation_dataset.csv"
        )
        data = source
    else:
        data = df

    features = [
        "daily_rainfall_mm",
        "rainfall_3day_mm",
        "rainfall_7day_mm",
        "latitude",
        "longitude",
        elevation_feature
    ]

    X = data[features]
    y = data["flood_label"]

    train_index, test_index = next(
        splitter.split(X, y, groups)
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42
    )

    model.fit(
        X.iloc[train_index],
        y.iloc[train_index]
    )

    predictions = model.predict(X.iloc[test_index])
    probabilities = model.predict_proba(X.iloc[test_index])[:, 1]

    y_test = y.iloc[test_index]

    results.append({
        "elevation_representation": elevation_feature,
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

print("\nELEVATION REPRESENTATION COMPARISON")
print("----------------------------------")
print(result_df.round(4).to_string(index=False))

result_df.to_csv(
    "datasets/processed/elevation_representation_comparison.csv",
    index=False
)

print("\nSaved: datasets/processed/elevation_representation_comparison.csv")