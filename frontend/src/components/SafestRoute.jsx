
import React, { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
  useMap
} from "react-leaflet";

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./SafestRoute.css";

function MapUpdater({ coordinates }) {
  const map = useMap();

  useEffect(() => {
    if (coordinates && coordinates.length > 0) {
      map.fitBounds(coordinates, { padding: [40, 40] });
    }
  }, [coordinates, map]);

  return null;
}

function SafestRoute({
  initialStart = "",
  initialDestination = ""
}) {
  const [start, setStart] = useState(initialStart);
  const [destination, setDestination] = useState(initialDestination);

  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setStart(initialStart);
    setDestination(initialDestination);
  }, [initialStart, initialDestination]);

  useEffect(() => {
    if (initialStart.trim() && initialDestination.trim()) {
      fetchRoute(initialStart, initialDestination);
    }
  }, [initialStart, initialDestination]);

  const fetchRoute = async (startLocation, destinationLocation) => {
    if (!startLocation.trim() || !destinationLocation.trim()) {
      setError("Please enter both starting location and destination.");
      return;
    }

    setLoading(true);
    setError("");
    setRouteData(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/safest-route?start=${encodeURIComponent(
          startLocation.trim()
        )}&destination=${encodeURIComponent(
          destinationLocation.trim()
        )}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to calculate the route."
        );
      }

      if (!data.flood_aware_route) {
        throw new Error("Flood-aware route is not available.");
      }

      setRouteData(data);

    } catch (err) {
      setError(err.message || "Unable to calculate the route.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchRoute(start, destination);
  };

  const openGoogleMaps = () => {
    if (!start.trim() || !destination.trim()) {
      setError("Please enter both starting location and destination.");
      return;
    }

    const googleMapsUrl =
      `https://www.google.com/maps/dir/?api=1` +
      `&origin=${encodeURIComponent(start.trim())}` +
      `&destination=${encodeURIComponent(destination.trim())}` +
      `&travelmode=driving`;

    window.open(googleMapsUrl, "_blank", "noopener,noreferrer");
  };

  const floodAwareRoute = routeData?.flood_aware_route;

  const getCoordinates = (route) => {
    if (!route || !Array.isArray(route.coordinates)) {
      return [];
    }

    return route.coordinates
      .map((point) => {
        if (Array.isArray(point) && point.length >= 2) {
          return [Number(point[0]), Number(point[1])];
        }

        if (point && point.lat !== undefined && point.lon !== undefined) {
          return [Number(point.lat), Number(point.lon)];
        }

        if (
          point &&
          point.latitude !== undefined &&
          point.longitude !== undefined
        ) {
          return [Number(point.latitude), Number(point.longitude)];
        }

        return null;
      })
      .filter(
        (point) =>
          point &&
          Number.isFinite(point[0]) &&
          Number.isFinite(point[1])
      );
  };

  const floodAwareCoordinates = getCoordinates(floodAwareRoute);

  const mapCenter =
    floodAwareCoordinates.length > 0
      ? floodAwareCoordinates[0]
      : [26.5, 87.5];

  const startIcon = L.divIcon({
    className: "route-map-marker",
    html: '<div style="background:#16a34a;color:white;border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-weight:bold;border:2px solid white;">S</div>',
    iconSize: [30, 30],
    iconAnchor: [15, 15]
  });

  const destinationIcon = L.divIcon({
    className: "route-map-marker",
    html: '<div style="background:#dc2626;color:white;border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-weight:bold;border:2px solid white;">D</div>',
    iconSize: [30, 30],
    iconAnchor: [15, 15]
  });

  return (
    <div className="safest-route-page">

      <div className="safest-route-header">
        <h2>Flood-Aware Route Recommendation</h2>

        <p>
          Find an experimental route based on estimated flood
          risk between your starting location and destination.
        </p>
      </div>

      <form
        className="safest-route-form"
        onSubmit={handleSubmit}
      >

        <div className="route-input-group">
          <label htmlFor="route-start">
            Starting Location
          </label>

          <input
            id="route-start"
            type="text"
            placeholder="Enter starting village or town"
            value={start}
            onChange={(event) => setStart(event.target.value)}
          />
        </div>

        <div className="route-input-group">
          <label htmlFor="route-destination">
            Destination
          </label>

          <input
            id="route-destination"
            type="text"
            placeholder="Enter destination"
            value={destination}
            onChange={(event) => setDestination(event.target.value)}
          />
        </div>

        <div className="route-action-buttons">

          <button
            type="submit"
            disabled={loading}
            className="find-route-button"
          >
            {loading ? "Calculating Route..." : "Find Flood-Aware Route"}
          </button>

          <button
            type="button"
            className="google-maps-button"
            onClick={openGoogleMaps}
          >
            Open Google Maps
          </button>

        </div>
      </form>

      {error && (
        <div className="route-error">
          {error}
        </div>
      )}

      {loading && (
        <div className="route-loading">
          Calculating flood-aware route. Please wait...
        </div>
      )}

      {floodAwareRoute && (
        <>

          <div className="route-results">

            <h3>Flood-Aware Route Details</h3>

            <div className="route-cards">

              <div className="route-card selected">

                <h4>Flood-Aware Route</h4>

                <p>
                  Distance:{" "}
                  <strong>
                    {Number(floodAwareRoute.distance_km).toFixed(2)} km
                  </strong>
                </p>

                <p>
                  Estimated Risk:{" "}
                  <strong>
                    {floodAwareRoute.estimated_risk !== undefined
                      ? `${(
                          Number(floodAwareRoute.estimated_risk) * 100
                        ).toFixed(2)}%`
                      : "Not available"}
                  </strong>
                </p>

              </div>

            </div>
          </div>

          <div className="selected-route-details">

            <h3>Selected Flood-Aware Route</h3>

            <p>
              <strong>Starting Location:</strong> {start}
            </p>

            <p>
              <strong>Destination:</strong> {destination}
            </p>

            <p>
              <strong>Distance:</strong>{" "}
              {Number(floodAwareRoute.distance_km).toFixed(2)} km
            </p>

            <p>
              <strong>Estimated Risk:</strong>{" "}
              {floodAwareRoute.estimated_risk !== undefined
                ? `${(
                    Number(floodAwareRoute.estimated_risk) * 100
                  ).toFixed(2)}%`
                : "Not available"}
            </p>

            {floodAwareRoute.warning && (
              <p>
                <strong>Route Warning:</strong>{" "}
                {floodAwareRoute.warning}
              </p>
            )}

          </div>

          <div className="route-map-section">

            <h3>Flood-Aware Route Map</h3>

            <div className="route-map-legend">
              <span>
                <i className="legend-green"></i>
                Flood-Aware Route
              </span>
            </div>

            {floodAwareCoordinates.length > 0 ? (

              <MapContainer
                center={mapCenter}
                zoom={10}
                scrollWheelZoom={true}
                className="safest-route-map"
              >

                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; CARTO'
                  url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                />

                {floodAwareCoordinates.length > 1 && (
                  <Polyline
                    positions={floodAwareCoordinates}
                    pathOptions={{
                      color: "#0d9488",
                      weight: 6,
                      opacity: 1
                    }}
                  />
                )}

                <Marker
                  position={floodAwareCoordinates[0]}
                  icon={startIcon}
                >
                  <Popup>Starting Location</Popup>
                </Marker>

                <Marker
                  position={
                    floodAwareCoordinates[
                      floodAwareCoordinates.length - 1
                    ]
                  }
                  icon={destinationIcon}
                >
                  <Popup>Destination</Popup>
                </Marker>

                <MapUpdater coordinates={floodAwareCoordinates} />

              </MapContainer>

            ) : (

              <p className="route-no-coordinates">
                Route coordinates are not available for map display.
              </p>

            )}

          </div>

        </>
      )}

      <div className="route-disclaimer">

        <strong>Important Safety Information</strong>

        <p>
          This route recommendation is an experimental research
          output based on available historical data and estimated
          flood risk. It is not a verified safe evacuation route.
          Google Maps uses its own routing system and may show a
          different route from the route calculated by this project.
          Always follow official weather alerts and local emergency
          instructions.
        </p>

      </div>

    </div>
  );
}

export default SafestRoute;
