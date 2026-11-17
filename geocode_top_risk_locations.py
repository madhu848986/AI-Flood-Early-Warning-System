import pandas as pd
import time
import json
from pathlib import Path
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "datasets" / "processed" / "koshi_all_grid_flood_predictions.csv"
OUTPUT_FILE = BASE_DIR / "datasets" / "processed" / "koshi_top_risk_locations_named.csv"
CACHE_FILE = BASE_DIR / "datasets" / "processed" / "location_name_cache.json"

data = pd.read_csv(INPUT_FILE)

top_locations = (
    data[data["risk_category"] == "High Risk"]
    .sort_values("flood_probability", ascending=False)
    .head(5)
    .copy()
)

if CACHE_FILE.exists():
    with open(CACHE_FILE, "r", encoding="utf-8") as file:
        cache = json.load(file)
else:
    cache = {}

geolocator = Nominatim(
    user_agent="koshi_flood_research_prototype"
)

reverse = RateLimiter(
    geolocator.reverse,
    min_delay_seconds=1.1,
    max_retries=2,
    error_wait_seconds=2
)

def get_location_name(row):
    key = f'{row["latitude"]:.4f},{row["longitude"]:.4f}'

    if key in cache:
        return cache[key]

    try:
        location = reverse(
            (row["latitude"], row["longitude"]),
            language="en",
            zoom=10,
            addressdetails=True
        )

        if location:
            address = location.raw.get("address", {})

            name = (
                address.get("village")
                or address.get("town")
                or address.get("city")
                or address.get("municipality")
                or address.get("suburb")
                or address.get("county")
                or "Locality not identified"
            )

            cache[key] = name
        else:
            cache[key] = "Locality not identified"

    except Exception as error:
        print(f"Could not identify {key}: {error}")
        cache[key] = "Locality not identified"

    return cache[key]


top_locations["area_name"] = top_locations.apply(
    get_location_name,
    axis=1
)

top_locations.to_csv(OUTPUT_FILE, index=False)

with open(CACHE_FILE, "w", encoding="utf-8") as file:
    json.dump(cache, file, indent=4, ensure_ascii=False)

print("\nTop risk locations with area names:")
print(
    top_locations[
        ["area_name", "latitude", "longitude", "flood_probability", "risk_category"]
    ].to_string(index=False)
)

print(f"\nSaved: {OUTPUT_FILE}")