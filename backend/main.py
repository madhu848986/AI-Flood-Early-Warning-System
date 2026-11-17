
from pathlib import Path
import json
import time

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.route_service import get_route_comparison
from backend.alert_scheduler import start_alert_scheduler

from backend.auth_service import (
    initialize_database,
    register_user,
    login_user,
    get_user_by_token,
    update_user_location,
    logout_user,
    get_users_with_locations,
    create_flood_alert,
    get_user_alerts,
    update_alert_status
)


app = FastAPI(
    title="FloodGuard AI API",
    description="Koshi Basin Flood Risk Research Prototype",
    version="1.0.0"
)

# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "datasets" / "processed"

FLOOD_FILE = DATA_DIR / "koshi_all_grid_flood_predictions.csv"
SHELTER_FILE = DATA_DIR / "koshi_shelter_recommendations.csv"
NAMED_LOCATIONS_FILE = DATA_DIR / "koshi_top_risk_locations_named.csv"
LOCATION_CACHE_FILE = DATA_DIR / "safest_place_location_cache.json"

geolocator = Nominatim(
    user_agent="koshi_flood_research_prototype"
)

last_reverse_request = 0


# ---------------- REQUEST MODELS ----------------

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    mobile: str = Field(min_length=10, max_length=15)
    address: str = Field(min_length=3, max_length=200)


class LoginRequest(BaseModel):
    username: str
    password: str


class LocationRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class FloodAlertRequest(BaseModel):
    risk_category: str = Field(min_length=1, max_length=50)
    flood_probability: float = Field(ge=0, le=1)
    message: str = Field(min_length=1, max_length=500)


# ---------------- DATABASE INITIALIZATION ----------------

@app.on_event("startup")
def startup_event():
    initialize_database()
    start_alert_scheduler()


# ---------------- HELPER FUNCTIONS ----------------

def load_csv(file_path):

    if not file_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Dataset not found: {file_path.name}"
        )

    return pd.read_csv(file_path)


def clean_records(dataframe):

    dataframe = dataframe.astype(object)
    dataframe = dataframe.where(pd.notna(dataframe), None)

    return dataframe.to_dict(orient="records")


def load_location_cache():

    if LOCATION_CACHE_FILE.exists():

        try:
            with open(
                LOCATION_CACHE_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError):
            return {}

    return {}


def save_location_cache(cache):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        LOCATION_CACHE_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            cache,
            file,
            indent=4,
            ensure_ascii=False
        )


def get_area_name(latitude, longitude):

    global last_reverse_request

    if latitude is None or longitude is None:
        return "Locality not identified"

    key = f"{latitude:.4f},{longitude:.4f}"

    cache = load_location_cache()

    if key in cache:
        return cache[key]

    area_name = "Locality not identified"

    try:

        elapsed = time.time() - last_reverse_request

        if elapsed < 1.1:
            time.sleep(1.1 - elapsed)

        location = geolocator.reverse(
            (latitude, longitude),
            exactly_one=True,
            language="en",
            timeout=10,
            zoom=10,
            addressdetails=True
        )

        last_reverse_request = time.time()

        if location:

            address = location.raw.get("address", {})

            area_name = (
                address.get("village")
                or address.get("town")
                or address.get("city")
                or address.get("municipality")
                or address.get("suburb")
                or address.get("county")
                or "Locality not identified"
            )

    except Exception as error:

        print(
            f"Reverse geocoding error for {key}: {error}"
        )

    cache[key] = area_name

    save_location_cache(cache)

    return area_name


# ---------------- HOME API ----------------

@app.get("/")
def home():

    return {
        "message": "FloodGuard AI backend is running",
        "project": "Koshi Basin Flood Early-Warning System"
    }


# ---------------- AUTHENTICATION APIs ----------------

@app.post("/api/auth/register")
def api_register(request: RegisterRequest):

    user_id = register_user(
        request.username.strip(),
        request.password,
        request.mobile.strip(),
        request.address.strip()
    )

    if user_id is None:

        raise HTTPException(
            status_code=409,
            detail="Username or mobile number already registered."
        )

    return {
        "message": "Registration successful",
        "user_id": user_id
    }


@app.post("/api/auth/login")
def api_login(request: LoginRequest):

    token = login_user(
        request.username.strip(),
        request.password
    )

    if token is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    return {
        "message": "Login successful",
        "token": token
    }


@app.get("/api/auth/me")
def api_me(authorization: str = Header(None)):

    if not authorization or not authorization.startswith("Bearer "):

        raise HTTPException(
            status_code=401,
            detail="Login required."
        )

    token = authorization[7:]

    user = get_user_by_token(token)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid session."
        )

    return dict(user)


@app.post("/api/auth/location")
def api_save_location(
    request: LocationRequest,
    authorization: str = Header(None)
):

    if not authorization or not authorization.startswith("Bearer "):

        raise HTTPException(
            status_code=401,
            detail="Login required."
        )

    token = authorization[7:]

    user = get_user_by_token(token)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid session."
        )

    update_user_location(
        user["id"],
        request.latitude,
        request.longitude
    )

    return {
        "message": "Location saved successfully",
        "latitude": request.latitude,
        "longitude": request.longitude
    }


@app.post("/api/auth/logout")
def api_logout(authorization: str = Header(None)):

    if not authorization or not authorization.startswith("Bearer "):

        raise HTTPException(
            status_code=401,
            detail="Login required."
        )

    token = authorization[7:]

    user = get_user_by_token(token)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid session."
        )

    logout_user(token)

    return {
        "message": "Logged out successfully"
    }


# ---------------- FLOOD ALERT APIs ----------------

@app.get("/api/alerts")
def api_get_alerts(authorization: str = Header(None)):

    if not authorization or not authorization.startswith("Bearer "):

        raise HTTPException(
            status_code=401,
            detail="Login required."
        )

    token = authorization[7:]

    user = get_user_by_token(token)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid session."
        )

    alerts = get_user_alerts(user["id"])

    return [
        dict(alert)
        for alert in alerts
    ]


@app.post("/api/alerts")
def api_create_alert(
    request: FloodAlertRequest,
    authorization: str = Header(None)
):

    if not authorization or not authorization.startswith("Bearer "):

        raise HTTPException(
            status_code=401,
            detail="Login required."
        )

    token = authorization[7:]

    user = get_user_by_token(token)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid session."
        )

    alert_id = create_flood_alert(
        user["id"],
        request.risk_category,
        request.flood_probability,
        request.message
    )

    return {
        "message": "Flood alert recorded successfully",
        "alert_id": alert_id
    }


# ---------------- DASHBOARD API ----------------

@app.get("/api/dashboard")
def dashboard():

    flood = load_csv(FLOOD_FILE)
    shelters = load_csv(SHELTER_FILE)

    high_risk = int(
        (flood["risk_category"] == "High Risk").sum()
    )

    lower_risk = int(
        (flood["risk_category"] == "Lower Risk").sum()
    )

    return {
        "total_grid_cells": len(flood),
        "high_risk_cells": high_risk,
        "lower_risk_cells": lower_risk,
        "total_shelters": len(shelters),
        "high_risk_shelters": int(
            (shelters["screening_risk_category"] == "High Risk").sum()
        ),
        "lower_risk_shelters": int(
            (shelters["screening_risk_category"] == "Lower Risk").sum()
        ),
        "average_flood_probability": round(
            float(flood["flood_probability"].mean()), 4
        ),
        "average_daily_rainfall_mm": round(
            float(flood["daily_rainfall_mm"].mean()), 3
        )
    }


# ---------------- FLOOD GRID API ----------------

@app.get("/api/flood-grid")
def flood_grid():

    flood = load_csv(FLOOD_FILE)

    return clean_records(flood)


# ---------------- SHELTER API ----------------

@app.get("/api/shelters")
def shelters():

    shelter_data = load_csv(SHELTER_FILE)

    records = clean_records(shelter_data)

    cache = load_location_cache()

    for shelter in records:

        latitude = shelter.get("latitude")
        longitude = shelter.get("longitude")

        if latitude is not None and longitude is not None:

            key = f"{float(latitude):.4f},{float(longitude):.4f}"

            shelter["location_name"] = cache.get(
                key,
                "Location details unavailable"
            )

        else:

            shelter["location_name"] = (
                "Location details unavailable"
            )

    return records


# ---------------- TOP RISK LOCATIONS API ----------------

@app.get("/api/top-risk-locations")
def top_risk_locations():

    locations = load_csv(NAMED_LOCATIONS_FILE)

    return clean_records(locations)


# ---------------- SAFEST PLACES API ----------------

@app.get("/api/safest-places")
def find_safest_places(place: str):

    if not place.strip():

        raise HTTPException(
            status_code=400,
            detail="Enter a village or town name."
        )

    try:

        result = geolocator.geocode(
            place.strip(),
            exactly_one=True,
            timeout=10,
            country_codes="np"
        )

    except Exception as error:

        print(
            "NOMINATIM GEOCODING ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=503,
            detail="Location search failed. Check backend terminal for details."
        )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail="Location not found. Try another village or town name."
        )

    print("SEARCHED LOCATION:", result.address)
    print("LATITUDE:", result.latitude)
    print("LONGITUDE:", result.longitude)

    try:

        flood = load_csv(FLOOD_FILE)

        required_columns = [
            "latitude",
            "longitude",
            "risk_category",
            "flood_probability"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in flood.columns
        ]

        if missing_columns:

            raise ValueError(
                f"Missing columns in flood dataset: {missing_columns}"
            )

        if flood.empty:

            raise ValueError(
                "Flood prediction dataset is empty."
            )

    except Exception as error:

        print(
            "FLOOD DATA ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to load flood prediction data."
        )

    try:

        flood["distance_km"] = flood.apply(
            lambda row: geodesic(
                (result.latitude, result.longitude),
                (row["latitude"], row["longitude"])
            ).km,
            axis=1
        )

    except Exception as error:

        print(
            "DISTANCE CALCULATION ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to calculate nearby locations."
        )

    nearby = flood[
        (flood["distance_km"] <= 20) &
        (flood["distance_km"] > 1)
    ].copy()

    lower_risk = nearby[
        nearby["risk_category"] == "Lower Risk"
    ].copy()

    lower_risk = lower_risk.sort_values(
        by=["distance_km", "flood_probability"]
    )

    if lower_risk.empty:
        return []

    try:

        lower_risk["area_name"] = lower_risk.apply(
            lambda row: get_area_name(
                row["latitude"],
                row["longitude"]
            ),
            axis=1
        )

    except Exception as error:

        print(
            "AREA NAME ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve nearby area names."
        )

    searched_name = place.strip().casefold()

    lower_risk = lower_risk[
        lower_risk["area_name"].apply(
            lambda name: str(name).strip().casefold() != searched_name
        )
    ]

    lower_risk = lower_risk.drop_duplicates(
        subset=["area_name"]
    ).head(5)

    print(
        "SAFE PLACES FOUND:",
        len(lower_risk)
    )

    return clean_records(lower_risk)


# ---------------- SAFEST ROUTE API ----------------

@app.get("/api/safest-route")
def safest_route(start: str, destination: str):

    if not start.strip() or not destination.strip():

        raise HTTPException(
            status_code=400,
            detail="Enter both starting point and destination."
        )

    try:

        return get_route_comparison(
            start.strip(),
            destination.strip()
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:

        print(
            "ROUTE CALCULATION ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=503,
            detail="Route calculation failed."
        )
