
import threading
import time
import pandas as pd
from geopy.distance import geodesic
from pathlib import Path

from backend.auth_service import (
    get_users_with_locations,
    create_flood_alert_with_status
)


BASE_DIR = Path(__file__).resolve().parent.parent

FLOOD_FILE = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "koshi_all_grid_flood_predictions.csv"
)

SHELTER_FILE = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "koshi_shelter_recommendations.csv"
)

CHECK_INTERVAL = 30 * 60
ALERT_THRESHOLD = 0.70
SEARCH_RADIUS_KM = 20

scheduler_started = False
scheduler_lock = threading.Lock()


def find_nearest_shelter(user_location):

    try:
        shelters = pd.read_csv(SHELTER_FILE)

        required_columns = [
            "latitude",
            "longitude",
            "screening_risk_category"
        ]

        if not all(column in shelters.columns for column in required_columns):
            raise ValueError("Required shelter columns are missing.")

        shelters["latitude"] = pd.to_numeric(
            shelters["latitude"], errors="coerce"
        )
        shelters["longitude"] = pd.to_numeric(
            shelters["longitude"], errors="coerce"
        )

        shelters = shelters.dropna(
            subset=["latitude", "longitude"]
        )

        shelters = shelters[
            shelters["screening_risk_category"].astype(str).str.strip()
            == "Lower Risk"
        ].copy()

        if shelters.empty:
            return "No listed lower-risk shelter found"

        shelters["distance_km"] = shelters.apply(
            lambda row: geodesic(
                user_location,
                (row["latitude"], row["longitude"])
            ).km,
            axis=1
        )

        nearest = shelters.sort_values(
            by="distance_km"
        ).iloc[0]

        name = nearest.get("name")

        if pd.isna(name) or not str(name).strip():
            name = (
                f"coordinates {nearest['latitude']:.4f}, "
                f"{nearest['longitude']:.4f}"
            )

        return (
            f"{name} "
            f"({nearest['distance_km']:.2f} km; "
            "field verification required)"
        )

    except Exception as error:
        print("SHELTER LOOKUP ERROR:", repr(error))
        return "Shelter information unavailable"


def check_user_flood_risk():

    print("Starting automatic flood-risk check...")

    try:
        flood = pd.read_csv(FLOOD_FILE)

        required_columns = [
            "latitude",
            "longitude",
            "risk_category",
            "flood_probability"
        ]

        if not all(column in flood.columns for column in required_columns):
            raise ValueError("Required flood prediction columns are missing.")

        flood["latitude"] = pd.to_numeric(
            flood["latitude"], errors="coerce"
        )
        flood["longitude"] = pd.to_numeric(
            flood["longitude"], errors="coerce"
        )
        flood["flood_probability"] = pd.to_numeric(
            flood["flood_probability"], errors="coerce"
        )

        flood = flood.dropna(
            subset=[
                "latitude",
                "longitude",
                "flood_probability",
                "risk_category"
            ]
        )

        users = get_users_with_locations()

        if not users:
            print("No users with saved locations found.")

        for user in users:

            if user["latitude"] is None or user["longitude"] is None:
                continue

            user_location = (
                float(user["latitude"]),
                float(user["longitude"])
            )

            nearby = flood.copy()

            nearby["distance_km"] = nearby.apply(
                lambda row: geodesic(
                    user_location,
                    (row["latitude"], row["longitude"])
                ).km,
                axis=1
            )

            nearby = nearby[
                nearby["distance_km"] <= SEARCH_RADIUS_KM
            ].copy()

            if nearby.empty:
                print(
                    f"No flood-grid data within {SEARCH_RADIUS_KM} km "
                    f"of user ID {user['id']}."
                )
                continue

            high_risk_cells = nearby[
                (nearby["risk_category"].astype(str).str.strip() == "High Risk")
                & (nearby["flood_probability"] >= ALERT_THRESHOLD)
            ].copy()

            if high_risk_cells.empty:
                print(
                    f"No qualifying high-risk cells near user ID {user['id']}."
                )
                continue

            highest_risk = high_risk_cells.sort_values(
                by="flood_probability",
                ascending=False
            ).iloc[0]

            probability = float(highest_risk["flood_probability"])
            latitude = float(highest_risk["latitude"])
            longitude = float(highest_risk["longitude"])
            distance = float(highest_risk["distance_km"])

            message = (
                "FloodGuard experimental model alert: High flood risk "
                "detected near your saved location. "
                f"Estimated model probability: {probability:.0%}. "
                f"Prediction grid location: ({latitude:.4f}, {longitude:.4f}). "
                f"Distance: {distance:.2f} km. "
                "This is not an official warning. Follow local authority "
                "instructions."
            )

            alert_id, is_new = create_flood_alert_with_status(
                user["id"],
                "High Risk",
                probability,
                message
            )

            if is_new:
                print(
                    f"New in-app flood alert created for user ID {user['id']}."
                )
            else:
                print(
                    f"Existing alert found for user ID {user['id']}."
                )

            print(
                f"High-risk cell found for user ID {user['id']}: "
                f"{probability:.0%}, {distance:.2f} km away. "
                f"Alert record ID: {alert_id}"
            )

        print("Automatic flood-risk check completed.")

    except Exception as error:
        print("AUTOMATIC FLOOD CHECK ERROR:", repr(error))


def scheduler_loop():

    while True:
        check_user_flood_risk()
        time.sleep(CHECK_INTERVAL)


def start_alert_scheduler():

    global scheduler_started

    with scheduler_lock:

        if scheduler_started:
            return

        scheduler_started = True

    thread = threading.Thread(
        target=scheduler_loop,
        daemon=True
    )

    thread.start()

    print(
        f"Flood alert scheduler started. "
        f"Interval: {CHECK_INTERVAL // 60} minutes."
    )
