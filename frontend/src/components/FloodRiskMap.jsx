
import { useEffect, useState } from 'react'
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap
} from 'react-leaflet'

import 'leaflet/dist/leaflet.css'
import './FloodRiskMap.css'

function FitMap({ locations }) {
  const map = useMap()

  useEffect(() => {
    if (locations.length > 0) {
      const bounds = locations.map(item => [
        Number(item.latitude),
        Number(item.longitude)
      ])

      map.fitBounds(bounds, { padding: [25, 25] })
    }
  }, [locations, map])

  return null
}

function FloodRiskMap() {
  const [locations, setLocations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('All')

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/flood-grid')
      .then(response => {
        if (!response.ok) {
          throw new Error('Unable to load flood risk locations')
        }
        return response.json()
      })
      .then(data => {
        setLocations(data)
        setLoading(false)
      })
      .catch(() => {
        setError('Unable to connect to the flood risk service.')
        setLoading(false)
      })
  }, [])

  const filteredLocations = locations.filter(item => {
    if (filter === 'All') return true
    if (filter === 'High Risk') return item.risk_category === 'High Risk'
    if (filter === 'Lower Risk') return item.risk_category === 'Lower Risk'
    return true
  })

  const highRisk = locations.filter(
    item => item.risk_category === 'High Risk'
  ).length

  const lowerRisk = locations.filter(
    item => item.risk_category === 'Lower Risk'
  ).length

  if (loading) {
    return <div className="map-message">Loading flood risk information...</div>
  }

  if (error) {
    return <div className="map-message error-message">{error}</div>
  }

  return (
    <div className="flood-map-page">
      <div className="map-heading">
        <div>
          <h2>Flood Risk Map</h2>
          <p>Explore estimated flood risk across the Koshi Basin.</p>
        </div>
        <span className="map-status">Experimental estimates</span>
      </div>

      <div className="map-summary">
        <div className="map-summary-card">
          <span>Total locations</span>
          <strong>{locations.length.toLocaleString()}</strong>
        </div>

        <div className="map-summary-card">
          <span>Higher risk</span>
          <strong className="high-text">{highRisk.toLocaleString()}</strong>
        </div>

        <div className="map-summary-card">
          <span>Lower risk</span>
          <strong className="low-text">{lowerRisk.toLocaleString()}</strong>
        </div>
      </div>

      <div className="map-filter">
        <span>Show locations:</span>
        {['All', 'High Risk', 'Lower Risk'].map(option => (
          <button
            key={option}
            className={filter === option ? 'selected-filter' : ''}
            onClick={() => setFilter(option)}
          >
            {option}
          </button>
        ))}
      </div>

      <div className="map-container">
        <MapContainer
          center={[27.0, 87.2]}
          zoom={7}
          scrollWheelZoom={true}
          className="flood-leaflet-map"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <FitMap locations={filteredLocations} />

          {filteredLocations.map((item, index) => {
            const isHigh = item.risk_category === 'High Risk'
            const probability = Number(item.flood_probability)

            return (
              <CircleMarker
                key={`${item.latitude}-${item.longitude}-${index}`}
                center={[
                  Number(item.latitude),
                  Number(item.longitude)
                ]}
                radius={5}
                pathOptions={{
                  color: isHigh ? '#b91c1c' : '#15803d',
                  fillColor: isHigh ? '#ef4444' : '#22c55e',
                  fillOpacity: 0.75,
                  weight: 1
                }}
              >
               <Popup>
  <div className="map-popup">
    <h3>{isHigh ? "Higher Flood Risk Area" : "Lower Flood Risk Area"}</h3>

    <div className={isHigh ? "popup-risk high" : "popup-risk low"}>
      {isHigh ? "Extra Caution Recommended" : "Relatively Lower Estimated Risk"}
    </div>

    <p>
      {isHigh
        ? "This area has a higher estimated flood risk based on the available historical data. Please stay alert and follow official local updates."
        : "This area has a lower estimated flood risk in the available data. However, flooding may still occur, so remain cautious."}
    </p>

    <h4>What should you do?</h4>

    {isHigh ? (
      <ul>
        <li>Monitor official weather and flood updates.</li>
        <li>Avoid flooded roads and low-lying areas.</li>
        <li>Follow instructions from local authorities.</li>
      </ul>
    ) : (
      <ul>
        <li>Continue monitoring local weather updates.</li>
        <li>Avoid walking or driving through floodwater.</li>
        <li>Follow official safety instructions.</li>
      </ul>
    )}

    <details>
      <summary>View location and technical details</summary>

      <p><strong>Latitude:</strong> {Number(item.latitude).toFixed(4)}</p>
      <p><strong>Longitude:</strong> {Number(item.longitude).toFixed(4)}</p>
      <p><strong>Model estimate:</strong> {(probability * 100).toFixed(2)}%</p>
      <p><strong>Daily rainfall:</strong> {Number(item.daily_rainfall_mm).toFixed(2)} mm</p>
      <p><strong>3-day rainfall:</strong> {Number(item.rainfall_3day_mm).toFixed(2)} mm</p>
      <p><strong>7-day rainfall:</strong> {Number(item.rainfall_7day_mm).toFixed(2)} mm</p>
      <p><strong>Elevation:</strong> {Number(item.elevation_mean_m).toFixed(1)} m</p>
    </details>

    <small>
      Experimental estimate based on historical data. This is not a live flood
      prediction or an official warning. Always follow government and local
      emergency alerts.
    </small>
  </div>
</Popup>              </CircleMarker>
            )
          })}
        </MapContainer>
      </div>

      <div className="map-legend">
        <span><i className="legend-dot high-dot"></i> Higher Risk</span>
        <span><i className="legend-dot low-dot"></i> Lower Risk</span>
      </div>

      <div className="map-disclaimer">
        <strong>Important information</strong>
        <p>
          These locations show experimental model-based risk estimates.
          They are not official flood warnings. Check local authority
          updates before making safety decisions.
        </p>
      </div>
    </div>
  )
}

export default FloodRiskMap
