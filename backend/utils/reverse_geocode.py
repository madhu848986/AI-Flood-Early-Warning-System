from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geolocator = Nominatim(
    user_agent="floodguard_ai_shelter_finder"
)

reverse = RateLimiter(
    geolocator.reverse,
    min_delay_seconds=1,
    max_retries=2,
    error_wait_seconds=2
)


def get_location_name(latitude, longitude):
    try:
        location = reverse(
            (latitude, longitude),
            exactly_one=True,
            language="en"
        )

        if location:
            address = location.raw.get("address", {})

            return (
                address.get("village")
                or address.get("town")
                or address.get("city")
                or address.get("suburb")
                or address.get("municipality")
                or address.get("county")
                or "Area name unavailable"
            )

        return "Area name unavailable"

    except Exception as e:
        print("Reverse geocoding error:", e)
        return "Area name unavailable"