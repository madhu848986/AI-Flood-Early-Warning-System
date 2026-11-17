
import { useEffect, useState } from 'react'
import FloodRiskMap from './components/FloodRiskMap'
import FloodForecast from './components/FloodForecast'
import SafestPlace from './components/SafestPlace'
import SafestRoute from './components/SafestRoute'
import ShelterFinder from './components/ShelterFinder'
import About from './components/About'
import './App.css'

const API = 'http://127.0.0.1:8000'

function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [activePage, setActivePage] = useState('Dashboard')

  const [token, setToken] = useState(
    localStorage.getItem('floodguard_token') || ''
  )
  const [user, setUser] = useState(null)
  const [authMode, setAuthMode] = useState('login')
  const [authError, setAuthError] = useState('')
  const [authMessage, setAuthMessage] = useState('')
  const [authLoading, setAuthLoading] = useState(false)

  const [alerts, setAlerts] = useState([])
  const [alertsLoading, setAlertsLoading] = useState(false)
  const [alertsError, setAlertsError] = useState('')

  const [form, setForm] = useState({
    username: '',
    password: '',
    mobile: '',
    address: ''
  })

  const [routeRequest, setRouteRequest] = useState({
    start: '',
    destination: ''
  })

  const authHeaders = {
    Authorization: `Bearer ${token}`
  }

  useEffect(() => {
    fetch(`${API}/api/dashboard`)
      .then(response => {
        if (!response.ok) throw new Error('Unable to load dashboard')
        return response.json()
      })
      .then(setData)
      .catch(err => setError(err.message))
  }, [])

  useEffect(() => {
    if (!token) {
      setUser(null)
      setAlerts([])
      return
    }

    fetch(`${API}/api/auth/me`, {
      headers: authHeaders
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Session expired. Please log in again.')
        }
        return response.json()
      })
      .then(setUser)
      .catch(() => {
        localStorage.removeItem('floodguard_token')
        setToken('')
        setUser(null)
      })
  }, [token])

  const fetchAlerts = async () => {
    if (!token) return

    setAlertsLoading(true)
    setAlertsError('')

    try {
      const response = await fetch(`${API}/api/alerts`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(
          result.detail || result.message || 'Unable to fetch flood alerts.'
        )
      }

      const alertList = Array.isArray(result)
        ? result
        : Array.isArray(result.alerts)
          ? result.alerts
          : []

      setAlerts(alertList)
    } catch (err) {
      setAlertsError(err.message)
    } finally {
      setAlertsLoading(false)
    }
  }

  useEffect(() => {
    if (token && activePage === 'Dashboard') {
      fetchAlerts()
    }
  }, [token, activePage])

  const menuItems = [
    'Dashboard',
    'Flood Risk Map',
    'Flood Forecast & Alerts',
    'Safest Place',
    'Safest Route',
    'Shelter Finder',
    'About & Emergency Information'
  ]

  const handleAuth = async event => {
    event.preventDefault()
    setAuthError('')
    setAuthMessage('')
    setAuthLoading(true)

    const endpoint = authMode === 'login'
      ? '/api/auth/login'
      : '/api/auth/register'

    const body = authMode === 'login'
      ? {
          username: form.username,
          password: form.password
        }
      : form

    try {
      const response = await fetch(`${API}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(
          result.detail || result.message || 'Authentication failed.'
        )
      }

      if (authMode === 'register') {
        setAuthMessage('Registration successful. Please log in.')
        setAuthMode('login')
        setForm({
          username: form.username,
          password: '',
          mobile: '',
          address: ''
        })
      } else {
        const newToken = result.access_token || result.token

        if (!newToken) {
          throw new Error('Login response did not contain a session token.')
        }

        localStorage.setItem('floodguard_token', newToken)
        setToken(newToken)
        setAuthMessage('Login successful.')
      }
    } catch (err) {
      setAuthError(err.message)
    } finally {
      setAuthLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await fetch(`${API}/api/auth/logout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
    } finally {
      localStorage.removeItem('floodguard_token')
      setToken('')
      setUser(null)
      setAlerts([])
      setActivePage('Dashboard')
    }
  }

  const handleViewFloodAwareRoute = (start, destination) => {
    setRouteRequest({ start, destination })
    setActivePage('Safest Route')
  }

  function renderPage() {
    if (activePage === 'Flood Risk Map') return <FloodRiskMap />
    if (activePage === 'Flood Forecast & Alerts') return <FloodForecast />

    if (activePage === 'Safest Place') {
      return <SafestPlace onViewRoute={handleViewFloodAwareRoute} />
    }

    if (activePage === 'Safest Route') {
      return (
        <SafestRoute
          initialStart={routeRequest.start}
          initialDestination={routeRequest.destination}
        />
      )
    }

    if (activePage === 'Shelter Finder') return <ShelterFinder />
    if (activePage === 'About & Emergency Information') return <About />

    if (!data) return <h2>{error || 'Loading dashboard...'}</h2>

    if (activePage === 'Dashboard') {
      const highPercent =
        data.high_risk_cells / data.total_grid_cells * 100

      const lowPercent =
        data.lower_risk_cells / data.total_grid_cells * 100

      return (
        <>
          <section className="welcome">
            <h2>Welcome to FloodGuard AI</h2>
            <p>
              Monitor estimated flood risk, rainfall and preliminary
              recommendations across the Koshi Basin.
            </p>
          </section>

          <section className="stats">
            <div className="stat-card">
              <p>Locations Assessed</p>
              <h2>{data.total_grid_cells.toLocaleString()}</h2>
              <small>Across the study area</small>
            </div>

            <div className="stat-card">
              <p>Higher Risk Locations</p>
              <h2>{data.high_risk_cells.toLocaleString()}</h2>
              <small>Experimental estimates</small>
            </div>

            <div className="stat-card">
              <p>Lower Risk Locations</p>
              <h2>{data.lower_risk_cells.toLocaleString()}</h2>
              <small>Experimental estimates</small>
            </div>

            <div className="stat-card">
              <p>Shelter Candidates</p>
              <h2>{data.total_shelters.toLocaleString()}</h2>
              <small>Require field verification</small>
            </div>
          </section>

          <section className="content-grid">
            <div className="panel">
              <h3>Flood Risk Overview</h3>

              <div className="risk-row">
                <span>Higher Risk</span>
                <strong>{data.high_risk_cells} locations</strong>
              </div>

              <div className="progress">
                <div
                  className="high-risk"
                  style={{ width: `${highPercent}%` }}
                />
              </div>

              <div className="risk-row">
                <span>Lower Risk</span>
                <strong>{data.lower_risk_cells} locations</strong>
              </div>

              <div className="progress">
                <div
                  className="low-risk"
                  style={{ width: `${lowPercent}%` }}
                />
              </div>

              <small>
                Distribution of experimental model estimates.
              </small>
            </div>

            <div className="panel">
              <h3>FloodGuard AI Services</h3>
              <ul className="module-list">
                <li>Flood Risk Monitoring</li>
                <li>Flood Forecast & Alerts</li>
                <li>Safest Place Recommendation</li>
                <li>Flood-Aware Route Planning</li>
                <li>Shelter Finder</li>
              </ul>
            </div>
          </section>

          <section className="stats">
            <div className="stat-card">
              <p>Average Estimated Flood Risk</p>
              <h2>
                {(data.average_flood_probability * 100).toFixed(2)}%
              </h2>
              <small>Model output average</small>
            </div>

            <div className="stat-card">
              <p>Average Daily Rainfall</p>
              <h2>
                {data.average_daily_rainfall_mm.toFixed(3)} mm
              </h2>
              <small>Study dataset average</small>
            </div>

            <div className="stat-card">
              <p>Lower Risk Shelter Candidates</p>
              <h2>{data.lower_risk_shelters}</h2>
              <small>Preliminary screening</small>
            </div>

            <div className="stat-card">
              <p>Higher Risk Shelter Candidates</p>
              <h2>{data.high_risk_shelters}</h2>
              <small>Require further assessment</small>
            </div>
          </section>

          <section className="panel flood-alert-panel">
            <div className="alert-heading">
              <h3>Flood Alerts</h3>

              <button
                onClick={fetchAlerts}
                disabled={alertsLoading}
              >
                {alertsLoading ? 'Refreshing...' : 'Refresh Alerts'}
              </button>
            </div>

            {alertsLoading && (
              <p>Loading flood alerts...</p>
            )}

            {alertsError && (
              <p className="auth-error">{alertsError}</p>
            )}

            {!alertsLoading && !alertsError && alerts.length === 0 && (
              <p>No flood alerts available.</p>
            )}

            {alerts.map((alert, index) => (
              <div
                className="test-alert"
                key={alert.id || index}
              >
                <h3>
                  ⚠️ {alert.risk_category || 'Flood Risk Alert'}
                </h3>

                <p>{alert.message}</p>

                <strong>
                  Estimated Model Probability:{' '}
                  {(Number(alert.flood_probability) * 100).toFixed(0)}%
                </strong>

                {alert.created_at && (
                  <p>
                    <small>
                      {new Date(alert.created_at).toLocaleString()}
                    </small>
                  </p>
                )}

                <small>
                  Experimental model alert — not an official warning.
                </small>
              </div>
            ))}
          </section>
        </>
      )
    }

    return (
      <section className="panel">
        <h2>{activePage}</h2>
        <p>
          This section is planned and will be implemented in the next steps.
        </p>
      </section>
    )
  }

  if (!user) {
    return (
      <div className="auth-page">
        <form className="auth-card" onSubmit={handleAuth}>
          <h1>FloodGuard AI</h1>
          <p>Flood Early Warning & Assistance</p>

          <h2>
            {authMode === 'login' ? 'User Login' : 'Create Account'}
          </h2>

          <label>Username</label>
          <input
            required
            minLength={3}
            value={form.username}
            onChange={e =>
              setForm({ ...form, username: e.target.value })
            }
          />

          <label>Password</label>
          <input
            required
            type="password"
            minLength={8}
            value={form.password}
            onChange={e =>
              setForm({ ...form, password: e.target.value })
            }
          />

          {authMode === 'register' && (
            <>
              <label>Mobile Number</label>
              <input
                required
                value={form.mobile}
                onChange={e =>
                  setForm({ ...form, mobile: e.target.value })
                }
              />

              <label>Address</label>
              <input
                required
                value={form.address}
                onChange={e =>
                  setForm({ ...form, address: e.target.value })
                }
              />
            </>
          )}

          {authError && <p className="auth-error">{authError}</p>}
          {authMessage && <p className="auth-success">{authMessage}</p>}

          <button type="submit" disabled={authLoading}>
            {authLoading
              ? 'Please wait...'
              : authMode === 'login'
                ? 'Login'
                : 'Register'}
          </button>

          <p>
            {authMode === 'login'
              ? "Don't have an account?"
              : 'Already registered?'}
            {' '}

            <button
              type="button"
              className="auth-switch"
              onClick={() => {
                setAuthMode(
                  authMode === 'login' ? 'register' : 'login'
                )
                setAuthError('')
                setAuthMessage('')
              }}
            >
              {authMode === 'login' ? 'Register' : 'Login'}
            </button>
          </p>
        </form>
      </div>
    )
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>FloodGuard AI</h2>
        <p className="subtitle">
          Flood Early Warning & Assistance
        </p>

        <nav>
          {menuItems.map(item => (
            <button
              key={item}
              className={activePage === item ? 'active' : ''}
              onClick={() => setActivePage(item)}
            >
              {item}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <p>Koshi Basin, Nepal</p>
          <small>Research Prototype</small>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>
              {activePage === 'Dashboard'
                ? 'Flood Monitoring Dashboard'
                : activePage}
            </h1>

            <p>
              AI-driven flood risk analysis and decision support
            </p>

            <small>Logged in as: {user.username}</small>
          </div>

          <div>
            <span className="status">● Experimental System</span>
            <button onClick={handleLogout}>
              Logout
            </button>
          </div>
        </header>

        {authMessage && (
          <p className="auth-success">{authMessage}</p>
        )}

        {authError && (
          <p className="auth-error">{authError}</p>
        )}

        {renderPage()}

        <section className="notice">
          <strong>Important safety information</strong>
          <p>
            Predictions and recommendations are experimental. They are not
            official flood warnings or confirmation of safe routes or shelters.
            Follow local authority instructions.
          </p>
        </section>

        <footer>
          AI-Driven Multimodal Flood Early-Warning and Dynamic Safe-Zone
          Recommendation System
        </footer>
      </main>
    </div>
  )
}

export default App
