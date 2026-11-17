import pandas as pd
import numpy as np

file = "datasets/processed/koshi_rainfall_accumulation_october_2021.csv"

df = pd.read_csv(file)
df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(["latitude", "longitude", "date"])

group = df.groupby(["latitude", "longitude"])["daily_rainfall_mm"]

df["calculated_3day"] = group.transform(
    lambda x: x.rolling(3, min_periods=3).sum()
)

df["calculated_7day"] = group.transform(
    lambda x: x.rolling(7, min_periods=7).sum()
)

for feature in ["rainfall_3day_mm", "rainfall_7day_mm"]:

    calculated = (
        df["calculated_3day"]
        if feature == "rainfall_3day_mm"
        else df["calculated_7day"]
    )

    valid = df[feature].notna() & calculated.notna()

    differences = np.abs(
        df.loc[valid, feature] - calculated[valid]
    )

    print("\nFEATURE:", feature)
    print("Valid comparisons:", valid.sum())
    print("Missing in original:", df[feature].isna().sum())
    print("Missing in recalculated:", calculated.isna().sum())
    print("Exact matches:", (differences == 0).sum())
    print(
        "Maximum difference:",
        differences.max() if len(differences) else "N/A"
    )

    print(
        "RESULT:",
        "PASS" if (
            df[feature].isna().equals(calculated.isna())
            and len(differences) > 0
            and (differences == 0).all()
        ) else "CHECK REQUIRED"
    )