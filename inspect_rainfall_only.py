import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import roc_auc_score, confusion_matrix

df = pd.read_csv(
    "datasets/processed/koshi_ml_dataset_with_elevation.csv"
)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm"
]

X = df[features]
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

for train_idx, test_idx in splitter.split(X, y, groups):
    if (
        y.iloc[train_idx].nunique() == 2
        and y.iloc[test_idx].nunique() == 2
    ):
        break

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42
)

model.fit(X.iloc[train_idx], y.iloc[train_idx])

probabilities = model.predict_proba(X.iloc[test_idx])[:, 1]
predictions = model.predict(X.iloc[test_idx])

print("ROC-AUC:", roc_auc_score(y.iloc[test_idx], probabilities))
print("Reversed probability ROC-AUC:", roc_auc_score(
    y.iloc[test_idx], 1 - probabilities
))

print("\nConfusion Matrix:")
print(confusion_matrix(y.iloc[test_idx], predictions))

print("\nAverage rainfall by actual label:")
print(
    df.groupby("flood_label")[features].mean().round(4)
)