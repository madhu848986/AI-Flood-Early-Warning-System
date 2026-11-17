
import React, { useEffect, useState } from "react";
import "./FloodForecast.css";

function FloodForecast() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/top-risk-locations")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Unable to load information");
        }
        return response.json();
      })
      .then((data) => {
        setLocations(data);
        setLoading(false);
      })
      .catch(() => {
        setError("Unable to load flood risk information. Please try again.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="forecast-message">Loading area information...</div>;
  }

  if (error) {
    return <div className="forecast-message error">{error}</div>;
  }

  const highRisk = locations.filter(
    (item) => item.risk_category === "High Risk"
  );

  const averageSevenDayRainfall =
    locations.reduce(
      (total, item) => total + Number(item.rainfall_7day_mm || 0),
      0
    ) / (locations.length || 1);

  const highestRiskLocations = [...highRisk]
    .sort(
      (a, b) =>
        Number(b.flood_probability) - Number(a.flood_probability)
    )
    .slice(0, 5);

  return (
    <div className="forecast-page">
      <div className="forecast-intro">
        <h2>Flood Risk Information</h2>
        <p>
          Understand which areas have been identified for extra attention.
        </p>
      </div>

      <div className="forecast-warning">
        <strong>Historical Data</strong>
        <p>
          This information is based on historical rainfall measurements
          and experimental research estimates. It is not a live forecast.
        </p>
      </div>

      <div className="forecast-cards">
        <div className="forecast-card">
          <span>Areas Needing Attention</span>
          <h2>{highRisk.length.toLocaleString("en-IN")}</h2>
          <small>Flagged by the research model</small>
        </div>

        <div className="forecast-card">
          <span>Average 7-Day Rainfall</span>
          <h2>{averageSevenDayRainfall.toFixed(2)} mm</h2>
          <small>Across available locations</small>
        </div>
      </div>

      <div className="forecast-panel">
        <h3>Areas Flagged for Extra Attention</h3>

        <p className="forecast-description">
          These locations received higher estimated risk scores in the
          historical research dataset.
        </p>

        <div className="forecast-table-wrapper">
          <table className="forecast-table">
            <thead>
              <tr>
                <th>Location</th>
                <th>7-Day Rainfall</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {highestRiskLocations.map((item, index) => (
                <tr key={index}>
                 <td>
                  <strong>{item.area_name}</strong>
                  </td>
                  <td>
                    {Number(item.rainfall_7day_mm).toFixed(2)} mm
                  </td>
                  <td>
                    <span className="forecast-risk-label">
                      Higher Risk
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="forecast-panel">
        <h3>What Should You Do?</h3>
        <ul className="forecast-action-list">
          <li>Check official weather and flood updates regularly.</li>
          <li>Avoid flooded roads and low-lying areas.</li>
          <li>Follow instructions from local authorities.</li>
        </ul>
      </div>

      <div className="forecast-disclaimer">
        <strong>Important Safety Information</strong>
        <p>
          These are historical research estimates, not live forecasts
          or official flood warnings. A higher-risk label does not
          confirm that flooding will occur. Always follow official
          emergency instructions.
        </p>
      </div>
    </div>
  );
}

export default FloodForecast;
