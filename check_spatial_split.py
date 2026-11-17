
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

file = "datasets/processed/koshi_ml_dataset.csv"

df = pd.read_csv(file)

df["spatial_group"] = (
    (df["latitude"] // 0.5).astype(int).astype(str)
    + "_"
    + (df["longitude"] // 0.5).astype(int).astype(str)
)

X = df.drop(columns=["flood_label", "spatial_group"])
y = df["flood_label"]
groups = df["spatial_group"]

splitter = GroupShuffleSplit(
    n_splits=10,
    test_size=0.25,
    random_state=42
)

print("SPATIAL TRAIN/TEST SPLIT CHECK")
print("=" * 45)

for train_idx, test_idx in splitter.split(X, y, groups):
    train_y = y.iloc[train_idx]
    test_y = y.iloc[test_idx]

    if train_y.nunique() == 2 and test_y.nunique() == 2:
        print("Training records:", len(train_idx))
        print("Testing records:", len(test_idx))
        print("\nTraining distribution:")
        print(train_y.value_counts())
        print("\nTesting distribution:")
        print(test_y.value_counts())
        print("\nSelected spatial groups:", groups.iloc[test_idx].nunique())
        break
else:
    print("No suitable split found in 10 attempts.")
    print("We need to inspect spatial group sizes.")
