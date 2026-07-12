import { useEffect, useState } from 'react'
import { api } from '../api'

interface Props {
  type: 'enrich' | 'email' | 'linkedin' | 'employees'
  companyIds: number[]
  onClose: () => void
  onApplied: () => void
}

const TITLES: Record<Props['type'], string> = {
  enrich: 'Verrijken via Claude',
  email: 'E-mails personaliseren via Claude',
  linkedin: 'LinkedIn-berichten personaliseren via Claude',
  employees: 'Medewerkers extraheren via Claude',
}

export default function AiModal({ type, companyIds, onClose, onApplied }: Props) {
  const [prompt, setPrompt] = useState('')
  const [payload, setPayload] = useState('')
  const [copied, setCopied] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<{ applied: number; skipped: number } | null>(null)

  useEffect(() => {
    api
      .post<{ prompt: string }>('/api/ai/prompt', { type, company_ids: companyIds })
      .then((r) => setPrompt(r.prompt))
      .catch((err) => setError(err instanceof Error ? err.message : 'Prompt genereren mislukt'))
  }, [type, companyIds])

  async function copy() {
    await navigator.clipboard.writeText(prompt)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  async function apply() {
    setBusy(true)
    setError('')
    try {
      const r = await api.post<{ applied: number; skipped: number }>('/api/ai/apply', {
        type,
        payload,
      })
      setResult(r)
      onApplied()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Toepassen mislukt')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h2>✨ {TITLES[type]}</h2>
          <button className="modal-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="info-box">
          Geen API-kosten: deze flow gebruikt jouw eigen <b>Claude-abonnement</b>. Kopieer de prompt, plak hem in{' '}
          <a href="https://claude.ai" target="_blank" rel="noreferrer">
            claude.ai
          </a>{' '}
          (of Claude Code), en plak Claude's JSON-antwoord hieronder terug.
        </div>

        {error && <div className="error-banner" style={{ marginTop: 12 }}>{error}</div>}

        <div className="step-row">
          <span className="step-badge">1</span> Kopieer de prompt ({companyIds.length} bedrijven)
        </div>
        <div className="prompt-box">{prompt || 'Prompt genereren…'}</div>
        <div style={{ marginTop: 8 }}>
          <button className="btn" onClick={copy} disabled={!prompt}>
            {copied ? '✓ Gekopieerd' : '📋 Kopieer prompt'}
          </button>
        </div>

        <div className="step-row">
          <span className="step-badge">2</span> Plak Claude's antwoord (JSON) hier terug
        </div>
        <label className="field">
          <textarea
            rows={6}
            value={payload}
            onChange={(e) => setPayload(e.target.value)}
            placeholder='```json&#10;[{"id": 1, ...}]&#10;```'
          />
        </label>

        {result && (
          <div className="info-box" style={{ marginTop: 12, background: '#ecfdf5' }}>
            ✓ Toegepast op {result.applied} bedrijven{result.skipped > 0 ? `, ${result.skipped} overgeslagen` : ''}.
          </div>
        )}

        <div className="modal-actions">
          <button className="btn" onClick={onClose}>
            Sluiten
          </button>
          <button className="btn primary" onClick={apply} disabled={busy || !payload.trim()}>
            {busy ? 'Bezig…' : '✨ Resultaat toepassen'}
          </button>
        </div>
      </div>
    </div>
  )
}
