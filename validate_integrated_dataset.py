import pandas as pd

path = "datasets/processed/koshi_rainfall_flood_integrated.csv"

df = pd.read_csv(path)

print("INTEGRATED DATASET VALIDATION")
print("=" * 45)

print("Total records:", len(df))
print("Unique grid cells:",
      df[["latitude", "longitude"]].drop_duplicates().shape[0])

print("\nRecords by date:")
print(df.groupby("date").size())

print("\nObservation availability by date:")
print(df.groupby("date")[
    "flood_observation_available"
].value_counts(dropna=False))

print("\nFlood indicator by date:")
print(df.groupby("date")[
    "observed_flood_present"
].value_counts(dropna=False))

print("\nDuplicate date-cell records:",
      df.duplicated(
          subset=["date", "latitude", "longitude"]
      ).sum())

print("\nUnique cells with valid flood observations:",
      df.loc[
          df["flood_observation_available"] == True,
          ["latitude", "longitude"]
      ].drop_duplicates().shape[0])

print("\nUnique cells with observed flood pixels:",
      df.loc[
          df["observed_flood_present"] == 1,
          ["latitude", "longitude"]
      ].drop_duplicates().shape[0])