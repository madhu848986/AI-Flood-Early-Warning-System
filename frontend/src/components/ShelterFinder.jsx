
import { useEffect, useState } from 'react'
import './ShelterFinder.css'

const API_URL = 'http://127.0.0.1:8000/api/shelters'

function ShelterFinder() {
  const [shelters, setShelters] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchShelters = async () => {
    try {
      setLoading(true)
      setError('')

      const response = await fetch(API_URL)

      if (!response.ok) {
        throw new Error('Unable to load shelter information')
      }

      const data = await response.json()

      if (!Array.isArray(data)) {
        throw new Error('Invalid shelter response format')
      }

      setShelters(data)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchShelters()
  }, [])

  const openGoogleMaps = (latitude, longitude) => {
    const lat = Number(latitude)
    const lon = Number(longitude)

    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
      return
    }

    const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}&travelmode=driving`

    window.open(url, '_blank', 'noopener,noreferrer')
  }

  const getRiskClass = (risk) => {
    if (risk === 'Higher Risk' || risk === 'High Risk') return 'high'
    if (risk === 'Moderate Risk') return 'moderate'
    if (risk === 'Lower Risk') return 'low'

    return 'unknown'
  }

  const getRiskLabel = (risk) => {
    if (risk === 'Higher Risk' || risk === 'High Risk') {
      return 'Higher Estimated Risk'
    }

    if (risk === 'Moderate Risk') {
      return 'Moderate Estimated Risk'
    }

    if (risk === 'Lower Risk') {
      return 'Lower Estimated Risk'
    }

    return 'Risk Unavailable'
  }

  const locationsToConfirm = shelters.filter(
    item => item.verification_status !== 'Verified'
  ).length

  return (
    <div className="shelter-page">

      <div className="shelter-header">
        <div>
          <h1>Shelter Finder</h1>
          <p>
            Find nearby shelter locations and check their estimated flood risk.
          </p>
        </div>

        <button
          className="refresh-button"
          onClick={fetchShelters}
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Refresh Shelters'}
        </button>
      </div>

      {loading && (
        <div className="shelter-message">
          Loading shelter information...
        </div>
      )}

      {error && (
        <div className="shelter-error">
          <strong>Unable to load shelters</strong>
          <p>{error}</p>
          <button
            className="refresh-button"
            onClick={fetchShelters}
          >
            Try Again
          </button>
        </div>
      )}

      {!loading && !error && shelters.length === 0 && (
        <div className="shelter-message">
          No shelter locations found.
        </div>
      )}

      {!loading && !error && shelters.length > 0 && (
        <>
          <div className="shelter-summary">

            <div className="summary-card">
              <h3>{shelters.length}</h3>
              <p>Shelter Locations</p>
            </div>

            <div className="summary-card">
              <h3>{locationsToConfirm}</h3>
              <p>Locations to Verify</p>
            </div>

          </div>

          <div className="shelter-grid">

            {shelters.map((item, index) => {
              const locationName =
                item.location_name ||
                item.place_name ||
                'Location details unavailable'

              const floodProbability =
                item.flood_probability != null &&
                Number.isFinite(Number(item.flood_probability))
                  ? `${(Number(item.flood_probability) * 100).toFixed(2)}%`
                  : 'Not available'

              const elevation =
                item.elevation_mean_m != null
                  ? `${item.elevation_mean_m} m`
                  : 'Not available'

              const hasCoordinates =
                Number.isFinite(Number(item.latitude)) &&
                Number.isFinite(Number(item.longitude)) &&
                item.latitude != null &&
                item.longitude != null

              return (
                <div
                  className="shelter-card"
                  key={item.osm_id || index}
                >

                  <div className="shelter-card-top">
                    <div>
                      <span className="shelter-rank">
                        Shelter #{item.recommendation_rank ?? index + 1}
                      </span>

                      <h2>
                        {locationName}
                      </h2>
                    </div>

                    <span
                      className={`risk-badge ${getRiskClass(item.risk_category)}`}
                    >
                      {getRiskLabel(item.risk_category)}
                    </span>
                  </div>

                  <div className="shelter-place">
                    <span>Village / Area</span>
                    <strong>{locationName}</strong>
                  </div>

                  <div className="shelter-details">

                    <div className="detail-box">
                      <span>Estimated Flood Risk</span>
                      <strong>{floodProbability}</strong>
                    </div>

                    <div className="detail-box">
                      <span>Elevation</span>
                      <strong>{elevation}</strong>
                    </div>

                  </div>

                  <div className="verification-box">
                    <strong>Before Visiting</strong>
                    <p>
                      Confirm that this location is an operational shelter
                      and is currently available with local authorities.
                    </p>
                  </div>

                  <button
                    className="shelter-map-button"
                    onClick={() =>
                      openGoogleMaps(
                        item.latitude,
                        item.longitude
                      )
                    }
                    disabled={!hasCoordinates}
                  >
                    Get Directions
                  </button>

                </div>
              )
            })}

          </div>
        </>
      )}

      <div className="shelter-disclaimer">
        <strong>Important Safety Information</strong>

        <p>
          Flood risk values are estimates. These are potential shelter
          locations, not confirmed operational emergency shelters.
          Verify availability locally and follow official emergency
          instructions.
        </p>
      </div>

    </div>
  )
}

export default ShelterFinder
