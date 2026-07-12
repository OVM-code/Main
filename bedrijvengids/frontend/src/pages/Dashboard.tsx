import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, clearToken } from '../api'
import type { Search, SearchDetail, Stats } from '../types'

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [searches, setSearches] = useState<Search[]>([])
  const [sector, setSector] = useState('')
  const [location, setLocation] = useState('')
  const [country, setCountry] = useState('België')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function load() {
    try {
      const [s, h] = await Promise.all([
        api.get<Stats>('/api/stats'),
        api.get<Search[]>('/api/searches'),
      ])
      setStats(s)
      setSearches(h)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Laden mislukt')
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!sector.trim() || !location.trim()) return
    setBusy(true)
    setError('')
    try {
      const result = await api.post<SearchDetail>('/api/searches', {
        sector: sector.trim(),
        location: location.trim(),
        country: country.trim() || 'België',
      })
      navigate(`/searches/${result.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Zoeken mislukt')
    } finally {
      setBusy(false)
    }
  }

  function logout() {
    clearToken()
    navigate('/login')
  }

  const pct = stats
    ? Math.min(100, (stats.monthly_credits_used / stats.monthly_credit_limit) * 100)
    : 0

  return (
    <div className="page">
      <div className="topbar">
        <div className="brand">
          Bedrijvengids<span>.AI</span>
        </div>
        <div className="spacer" />
        <Link to="/personen" className="btn">
          👥 Zoeken op personen
        </Link>
        <button className="btn" onClick={logout}>
          [→ Uitloggen
        </button>
      </div>

      <div className="stat-grid">
        <div className="card stat-card">
          <div className="stat-icon">🔍</div>
          <div>
            <div className="stat-label">Zoekopdrachten</div>
            <div className="stat-value">{stats?.search_count ?? '—'}</div>
          </div>
        </div>
        <div className="card stat-card">
          <div className="stat-icon">📈</div>
          <div>
            <div className="stat-label">Totaal bedrijven</div>
            <div className="stat-value">{stats?.company_count ?? '—'}</div>
          </div>
        </div>
        <div className="card stat-card" style={{ flex: 1 }}>
          <div className="stat-icon">⚡</div>
          <div style={{ flex: 1 }}>
            <div className="stat-label">Maandelijks verbruik</div>
            <div className="stat-value">
              {stats?.monthly_credits_used ?? '—'}{' '}
              <span className="of">/ {stats?.monthly_credit_limit?.toLocaleString('nl-BE') ?? ''}</span>
            </div>
            <div className="progress">
              <div style={{ width: `${pct}%` }} />
            </div>
            <div className="hint">Reset op 1e van de maand</div>
          </div>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <form className="card" style={{ marginBottom: 16 }} onSubmit={submit}>
        <div className="section-title">🔍 Nieuwe zoekopdracht</div>
        <div className="section-sub">Vul de sector en locatie in om bedrijven te zoeken</div>
        <div className="form-row">
          <label className="field">
            Sector
            <input
              value={sector}
              onChange={(e) => setSector(e.target.value)}
              placeholder="bijv. bakker, kapper, slager"
            />
          </label>
          <label className="field">
            Locatie (gemeente, provincie)
            <input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="bijv. Sint-Truiden, Limburg"
            />
          </label>
          <label className="field">
            Land
            <input
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              placeholder="bijv. België, Nederland"
            />
          </label>
        </div>
        <button className="btn primary" disabled={busy}>
          {busy ? (
            <>
              <span className="spin">◌</span> Live zoeken… (kan even duren)
            </>
          ) : (
            '🔍 Zoeken'
          )}
        </button>
      </form>

      <div className="card">
        <div className="section-title">🕓 Zoekgeschiedenis</div>
        <div className="section-sub">Klik op een zoekopdracht om resultaten te bekijken</div>
        {searches.length === 0 && <div className="empty">Nog geen zoekopdrachten</div>}
        {searches.map((s) => (
          <div key={s.id} className="history-item" onClick={() => navigate(`/searches/${s.id}`)}>
            <div className="history-date">
              {new Date(s.created_at).toLocaleDateString('nl-BE')}
            </div>
            <div className="history-query">
              {s.sector} in {s.location}
            </div>
            <div className="history-credits">{s.credits_used} cr</div>
            <div className="count-badge">{s.company_count}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
