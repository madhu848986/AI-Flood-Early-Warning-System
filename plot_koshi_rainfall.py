
import pandas as pd
import matplotlib.pyplot as plt

file_path = (
    "datasets/processed/"
    "koshi_rainfall_september_2020.csv"
)

df = pd.read_csv(file_path, parse_dates=["date"])

daily = (
    df.groupby("date")["precipitation_mm_per_day"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(9, 5))
plt.plot(
    daily["date"],
    daily["precipitation_mm_per_day"],
    marker="o"
)

plt.title("Mean Daily Precipitation in the Koshi Study Area")
plt.xlabel("Date")
plt.ylabel("Mean precipitation (mm/day)")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

output_path = (
    "datasets/processed/"
    "koshi_daily_rainfall.png"
)

plt.savefig(output_path, dpi=300)
plt.show()

print("\nDaily mean precipitation:")
print(daily.to_string(index=False))
print("\nGraph saved to:", output_path)
