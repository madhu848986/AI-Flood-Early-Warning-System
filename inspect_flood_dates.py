import pandas as pd
from pathlib import Path

folder = Path("datasets/processed")

df = pd.read_csv(folder / "koshi_rainfall_flood_integrated.csv")

print("FLOOD OBSERVATIONS BY DATE")
print("=" * 50)

for date, group in df.groupby("date"):
    valid = group[group["flood_observation_available"] == True]

    print("\nDate:", date)
    print("Total grid cells:", len(group))
    print("Valid observations:", len(valid))
    print("Missing observations:", len(group) - len(valid))

    if len(valid) > 0:
        print("Flood present:", (valid["observed_flood_present"] == 1).sum())
        print("No flood:", (valid["observed_flood_present"] == 0).sum())

print("\nEVENT DATASET CHECK")
print("=" * 50)

event = pd.read_csv(folder / "koshi_event_analysis_dataset.csv")
pre_event = pd.read_csv(folder / "koshi_pre_event_flood_dataset.csv")

print("Event dataset rows:", len(event))
print("Pre-event dataset rows:", len(pre_event))

print("Same coordinates:",
      event[["latitude", "longitude"]].equals(
          pre_event[["latitude", "longitude"]]
      ))

print("\nEvent label counts:")
print(event["flood_label"].value_counts())

print("\nPre-event label counts:")
print(pre_event["flood_label"].value_counts())