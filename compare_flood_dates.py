import pandas as pd
from pathlib import Path

folder = Path("datasets/processed")

df = pd.read_csv(
    folder / "koshi_rainfall_flood_integrated.csv"
)

valid = df[df["flood_observation_available"] == True].copy()

pivot = valid.pivot(
    index=["latitude", "longitude"],
    columns="date",
    values="observed_flood_present"
)

dates = sorted(pivot.columns)

print("DATE COMPARISON")
print("=" * 50)

if len(dates) == 2:
    first = dates[0]
    second = dates[1]

    comparison = pivot.dropna()

    print("First date:", first)
    print("Second date:", second)
    print("Comparable grid cells:", len(comparison))

    print(
        "Labels unchanged:",
        (comparison[first] == comparison[second]).sum()
    )

    print(
        "Changed from no flood to flood:",
        ((comparison[first] == 0) &
         (comparison[second] == 1)).sum()
    )

    print(
        "Changed from flood to no flood:",
        ((comparison[first] == 1) &
         (comparison[second] == 0)).sum()
    )

    print("\nLabel transition table:")
    print(pd.crosstab(
        comparison[first],
        comparison[second],
        rownames=["First date"],
        colnames=["Second date"]
    ))

print("\nRAINFALL COMPARISON")
print("=" * 50)

rain = pd.read_csv(
    folder / "koshi_rainfall_accumulation_october_2021.csv"
)

rain_summary = rain.groupby("date").agg(
    average_daily_rainfall=("daily_rainfall_mm", "mean"),
    average_3day_rainfall=("rainfall_3day_mm", "mean"),
    average_7day_rainfall=("rainfall_7day_mm", "mean")
)

print(rain_summary)