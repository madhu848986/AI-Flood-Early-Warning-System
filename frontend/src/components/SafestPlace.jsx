
import React, { useState } from "react";
import "./SafestPlace.css";

function SafestPlace({ onViewRoute }) {
  const [search, setSearch] = useState("");
  const [locations, setLocations] = useState([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const findPlaces = async (event) => {
    event.preventDefault();

    const place = search.trim();

    if (!place) {
      setError("Please enter a village or town name.");
      return;
    }

    setLoading(true);
    setError("");
    setLocations([]);
    setSearched(false);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/safest-places?place=${encodeURIComponent(place)}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to search for this place."
        );
      }

      setLocations(Array.isArray(data) ? data : []);
      setSearched(true);

    } catch (err) {
      setError(err.message || "Unable to search. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const viewFloodAwareRoute = (item) => {
    const start = search.trim();
    const destination = item.area_name?.trim();

    console.log("Selected area:", item);
    console.log("Starting location:", start);
    console.log("Destination:", destination);

    if (!start || !destination) {
      setError("Starting location or destination is unavailable.");
      return;
    }

    if (typeof onViewRoute !== "function") {
      setError("Route navigation is not configured. Please check App.jsx.");
      console.error("onViewRoute callback is missing.");
      return;
    }

    setError("");

    onViewRoute(start, destination);
  };

  return (
    <div className="safest-place-page">

      <div className="safest-place-intro">
        <h2>Find Comparatively Lower-Risk Areas</h2>

        <p>
          Enter your village or town name to explore nearby areas
          with comparatively lower estimated flood risk.
        </p>
      </div>

      <form className="place-search-form" onSubmit={findPlaces}>
        <label htmlFor="place-search">
          Village or Town Name
        </label>

        <div className="place-search-row">
          <input
            id="place-search"
            type="text"
            placeholder="Example: Biratnagar"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <button type="submit" disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </form>

      {error && (
        <p className="place-error">{error}</p>
      )}

      {searched && locations.length === 0 && (
        <div className="place-empty">
          No nearby lower-risk areas were found.
          Try another village or town.
        </div>
      )}

      {locations.length > 0 && (
        <div className="place-results">

          <h3>Nearby Lower-Risk Areas</h3>

          <p className="place-results-description">
            These areas have comparatively lower estimated flood
            risk in the available historical research data.
          </p>

          <div className="place-results-grid">
            {locations.map((item, index) => (
              <div className="place-result-card" key={index}>

                <div className="place-card-top">
                  <h4>{item.area_name}</h4>

                  <span className="place-status">
                    Lower Estimated Risk
                  </span>
                </div>

                <div className="place-detail">
                  <span>Distance from searched town</span>

                  <strong>
                    {Number(item.distance_km).toFixed(2)} km
                  </strong>
                </div>

                <div className="place-detail">
                  <span>Estimated Flood Risk</span>

                  <strong>
                    {(Number(item.flood_probability) * 100).toFixed(2)}%
                  </strong>
                </div>

                <div className="place-card-note">
                  Comparatively lower estimated risk
                  based on historical data.
                </div>

                <button
                  type="button"
                  className="place-directions-button"
                  onClick={() => viewFloodAwareRoute(item)}
                >
                  View Flood-Aware Route
                </button>

              </div>
            ))}
          </div>
        </div>
      )}

      <div className="place-disclaimer">
        <strong>Important Safety Information</strong>

        <p>
          These are experimental research estimates based on
          historical data. Lower estimated risk does not mean
          a location is completely safe. Conditions may change.
          Route recommendations are experimental and are not
          verified safe evacuation routes. Always follow official
          weather alerts and local emergency instructions.
        </p>
      </div>

    </div>
  );
}

export default SafestPlace;
