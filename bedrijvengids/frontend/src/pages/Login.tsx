import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, setToken } from '../api'

export default function Login() {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const { token } = await api.post<{ token: string }>('/api/auth/login', { password })
      setToken(token)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Inloggen mislukt')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <h1>
          Bedrijvengids<span style={{ color: 'var(--blue)' }}>.AI</span>
        </h1>
        <div className="sub">Minder research, meer gesprekken.</div>
        {error && <div className="error-banner">{error}</div>}
        <label className="field">
          Wachtwoord
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Wachtwoord"
            autoFocus
          />
          <div className="sub">Standaard: demo (instelbaar via BG_PASSWORD)</div>
        </label>
        <button className="btn primary" style={{ width: '100%', marginTop: 14, justifyContent: 'center' }} disabled={busy}>
          {busy ? 'Bezig…' : 'Inloggen'}
        </button>
      </form>
    </div>
  )
}
