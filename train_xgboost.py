import pandas as pd
import joblib

from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)

from xgboost import XGBClassifier

df = pd.read_csv(
    "datasets/processed/koshi_ml_dataset.csv"
)

df["spatial_group"] = (
    (df["latitude"] // 0.5).astype(int).astype(str)
    + "_"
    + (df["longitude"] // 0.5).astype(int).astype(str)
)

features = [
    "daily_rainfall_mm",
    "rainfall_3day_mm",
    "rainfall_7day_mm",
    "latitude",
    "longitude"
]

X = df[features]
y = df["flood_label"]
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
else:
    raise ValueError("No suitable spatial split found.")

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]
y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

model = XGBClassifier(
    n_estimators=200,
    max_depth=3,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

print("XGBoost Evaluation")
print("------------------")
print("Accuracy:", accuracy_score(y_test, predictions))
print(
    "Balanced Accuracy:",
    balanced_accuracy_score(y_test, predictions)
)
print("ROC-AUC:", roc_auc_score(y_test, probabilities))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        target_names=["No Flood", "Flood"],
        zero_division=0
    )
)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

joblib.dump(
    model,
    "datasets/processed/xgboost_baseline.pkl"
)

print("\nXGBoost model saved successfully.")