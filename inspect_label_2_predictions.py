import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit

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

model.fit(X.iloc[train_idx], y.iloc[train_idx])

probabilities = model.predict_proba(
    X.iloc[test_idx]
)[:, 1]

result = df.iloc[test_idx][
    ["latitude", "longitude", "label_2"]
].copy()

result["predicted_probability"] = probabilities
result["predicted_label"] = (
    result["predicted_probability"] >= 0.5
).astype(int)

result = result.sort_values(
    "predicted_probability",
    ascending=False
)

print("LABEL 2 TEST PREDICTIONS")
print("------------------------")
print(result.to_string(index=False))

result.to_csv(
    "datasets/processed/label_2_test_predictions.csv",
    index=False
)

print("\nSaved: datasets/processed/label_2_test_predictions.csv")