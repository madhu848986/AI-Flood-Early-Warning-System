import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit

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

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude",
    "elevation_m"
]

X = df[features]
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
    X.iloc[train_idx],
    y.iloc[train_idx]
)

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print("\nFEATURE IMPORTANCE")
print("------------------")
print(importance.to_string(index=False))

importance.to_csv(
    "datasets/processed/elevation_feature_importance.csv",
    index=False
)

print("\nSaved: datasets/processed/elevation_feature_importance.csv")