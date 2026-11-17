
from pathlib import Path
import json
import time

import pandas as pd
from geopy.geocoders import Nominatim


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datasets" / "processed"

SHELTER_FILE = DATA_DIR / "koshi_shelter_recommendations.csv"
CACHE_FILE = DATA_DIR / "safest_place_location_cache.json"

geolocator = Nominatim(
    user_agent="koshi_flood_research_prototype"
)


def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}

    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(cache, file, indent=4, ensure_ascii=False)


def get_location_name(latitude, longitude):
    try:
        location = geolocator.reverse(
            (latitude, longitude),
            exactly_one=True,
            language="en",
            timeout=15,
            zoom=10,
            addressdetails=True
        )

        if location:
            address = location.raw.get("address", {})

            return (
                address.get("village")
                or address.get("town")
                or address.get("city")
                or address.get("municipality")
                or address.get("suburb")
                or address.get("county")
                or "Locality not identified"
            )

    except Exception as error:
        print(f"Lookup failed: {error}")

    return "Locality not identified"


def main():
    shelters = pd.read_csv(SHELTER_FILE)
    cache = load_cache()

    total = len(shelters)
    completed = 0
    last_request = 0

    for _, shelter in shelters.iterrows():

        latitude = shelter["latitude"]
        longitude = shelter["longitude"]

        if pd.isna(latitude) or pd.isna(longitude):
            continue

        key = f"{latitude:.4f},{longitude:.4f}"

        if key in cache:
            continue

        elapsed = time.time() - last_request

        if elapsed < 1.1:
            time.sleep(1.1 - elapsed)

        name = get_location_name(latitude, longitude)
        last_request = time.time()

        cache[key] = name
        completed += 1

        if completed % 10 == 0:
            save_cache(cache)

        print(
            f"Processed {completed} new locations | "
            f"Current shelter: {name}"
        )

    save_cache(cache)

    print("\nLocation cache generation completed.")
    print(f"Total shelter records: {total}")
    print(f"New locations processed: {completed}")
    print(f"Total cached locations: {len(cache)}")


if __name__ == "__main__":
    main()
