import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Template } from '../types'

interface Props {
  kind: 'email' | 'linkedin'
  onClose: () => void
}

export default function TemplateModal({ kind, onClose }: Props) {
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [personalization, setPersonalization] = useState<'basic' | 'ai'>('basic')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .get<Template>(`/api/templates/${kind}`)
      .then((t) => {
        setSubject(t.subject ?? '')
        setBody(t.body)
        setPersonalization(t.personalization)
      })
      .catch(() => {})
  }, [kind])

  async function save() {
    setBusy(true)
    setError('')
    try {
      await api.put(`/api/templates/${kind}`, {
        subject: kind === 'email' ? subject : null,
        body,
        personalization,
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Opslaan mislukt')
    } finally {
      setBusy(false)
    }
  }

  const title = kind === 'email' ? 'E-mail Template' : 'LinkedIn Template'

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal wide" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h2>📄 {title}</h2>
          <button className="modal-close" onClick={onClose}>
            ✕
          </button>
        </div>
        {error && <div className="error-banner">{error}</div>}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          <div>
            <div className="section-sub">
              Maak een basis {kind === 'email' ? 'e-mail' : 'LinkedIn'} template die wordt gebruikt wanneer je op een
              prospect klikt. De template wordt automatisch gepersonaliseerd op basis van de beschikbare prospect data.
            </div>
            {kind === 'email' && (
              <label className="field" style={{ marginBottom: 12 }}>
                Onderwerp
                <input value={subject} onChange={(e) => setSubject(e.target.value)} />
                <div className="sub">Gebruik {'{bedrijfsnaam}'} of {'{zaakvoerder}'} om automatisch in te vullen</div>
              </label>
            )}
            <label className="field">
              {kind === 'email' ? 'E-mail inhoud' : 'Bericht'}
              <textarea rows={12} value={body} onChange={(e) => setBody(e.target.value)} />
              <div className="sub">
                Beschikbare placeholders: {'{bedrijfsnaam}'}, {'{zaakvoerder}'}, {'{gemeente}'}
              </div>
            </label>
          </div>
          <div>
            <div style={{ fontWeight: 600, marginBottom: 10 }}>Personalisatie niveau</div>
            <div
              className={`option-card ${personalization === 'basic' ? 'selected' : ''}`}
              onClick={() => setPersonalization('basic')}
            >
              <input type="radio" checked={personalization === 'basic'} readOnly />
              <div>
                <b>Basis personalisatie</b>
                <div className="sub">
                  Vervangt alleen {'{bedrijfsnaam}'}, {'{zaakvoerder}'} en {'{gemeente}'} met de prospect data. Snel en
                  voorspelbaar.
                </div>
              </div>
            </div>
            <div
              className={`option-card ${personalization === 'ai' ? 'selected' : ''}`}
              onClick={() => setPersonalization('ai')}
            >
              <input type="radio" checked={personalization === 'ai'} readOnly />
              <div>
                <b>AI personalisatie</b>
                <div className="sub">
                  Past ~20% van de {kind === 'email' ? 'e-mail' : 'boodschap'} aan op basis van de bedrijfsomschrijving
                  en sector. Creëert relevantere, contextbewuste berichten — via jouw Claude-abonnement (knop
                  "AI via Claude" in de lijst), zonder API-kosten.
                </div>
              </div>
            </div>
            <div className="info-box" style={{ marginTop: 14 }}>
              <b>ℹ️ Hoe werkt het?</b>
              <br />
              {kind === 'email' ? (
                <>
                  Wanneer je op een e-mailadres klikt in de prospect lijst, wordt je standaard e-mailprogramma geopend
                  met het "Aan" veld, onderwerp en e-mail body automatisch ingevuld. Je hebt altijd de controle en
                  verstuurt de e-mail handmatig.
                </>
              ) : (
                <>
                  Per prospect kan je het gepersonaliseerde bericht kopiëren en het LinkedIn-profiel openen. Je plakt en
                  verstuurt het bericht zelf op LinkedIn.
                </>
              )}
            </div>
          </div>
        </div>
        <div className="modal-actions">
          <button className="btn" onClick={onClose}>
            Annuleren
          </button>
          <button className="btn primary" onClick={save} disabled={busy || !body.trim()}>
            💾 Template opslaan
          </button>
        </div>
      </div>
    </div>
  )
}
