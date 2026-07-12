import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import type { Company, Employee, Message } from '../types'
import AiModal from './AiModal'

interface Props {
  company: Company
  onClose: () => void
}

function levelClass(level: string | null): string {
  if (level === 'C-Level') return 'level-badge c-level'
  if (level === 'Directeur') return 'level-badge directeur'
  return 'level-badge'
}

export default function EmployeesModal({ company, onClose }: Props) {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [busy, setBusy] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState('')
  const [showAi, setShowAi] = useState(false)

  const load = useCallback(() => {
    api
      .get<Employee[]>(`/api/companies/${company.id}/employees`)
      .then(setEmployees)
      .catch(() => {})
  }, [company.id])

  useEffect(() => {
    load()
  }, [load])

  async function find() {
    setBusy(true)
    setError('')
    try {
      const result = await api.post<Employee[]>(`/api/companies/${company.id}/employees/find`)
      setEmployees(result)
      setSearched(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Zoeken mislukt')
      setSearched(true)
    } finally {
      setBusy(false)
    }
  }

  async function prepareMail(employee: Employee) {
    const message = await api.get<Message>(`/api/companies/${company.id}/message?kind=email`)
    const to = employee.email ?? company.email ?? ''
    const body = message.body.replace(/^Beste[^,\n]*,?/, `Beste ${employee.name},`)
    window.location.href = `mailto:${to}?subject=${encodeURIComponent(message.subject ?? '')}&body=${encodeURIComponent(body)}`
  }

  function copyName(employee: Employee) {
    navigator.clipboard.writeText(`${employee.name}${employee.role ? ` — ${employee.role}` : ''}`)
  }

  function linkedinSearch(employee: Employee) {
    if (employee.linkedin) return window.open(employee.linkedin, '_blank')
    const q = encodeURIComponent(`${employee.name} ${company.name}`)
    window.open(`https://www.linkedin.com/search/results/people/?keywords=${q}`, '_blank')
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h2>👥 Medewerkers</h2>
          <button className="modal-close" onClick={onClose}>
            ✕
          </button>
        </div>
        <div style={{ marginBottom: 12 }}>
          <b>{company.name}</b>
          {company.website && (
            <>
              {' '}
              <a href={company.website} target="_blank" rel="noreferrer">
                {company.website.replace(/^https?:\/\/(www\.)?/, '')} ↗
              </a>
            </>
          )}
          <div className="muted" style={{ fontSize: 13, marginTop: 2 }}>
            {employees.length} medewerkers gevonden
          </div>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
          <button className="btn primary small" onClick={find} disabled={busy || !company.website}>
            {busy ? 'Team-pagina doorzoeken…' : "🔍 Vind medewerkers"}
          </button>
          <button className="btn small" onClick={() => setShowAi(true)}>
            ✨ Betere extractie via Claude
          </button>
        </div>

        {employees.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Naam</th>
                  <th>Functie</th>
                  <th>Niveau</th>
                  <th>Acties</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((e) => (
                  <tr key={e.id}>
                    <td>
                      <b>{e.name}</b>
                    </td>
                    <td>{e.role ?? '-'}</td>
                    <td>{e.level ? <span className={levelClass(e.level)}>{e.level}</span> : '-'}</td>
                    <td className="nowrap">
                      <button className="icon-btn" title="Bereid mail voor" onClick={() => prepareMail(e)}>
                        ✉️
                      </button>
                      <button className="icon-btn" title="Kopieer naam" onClick={() => copyName(e)}>
                        📋
                      </button>
                      <button className="icon-btn" title="Zoek op LinkedIn" onClick={() => linkedinSearch(e)}>
                        💼
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {employees.length === 0 && searched && !busy && (
          <div className="empty">
            Geen medewerkers gevonden op de website. Probeer "Betere extractie via Claude" — die leest de ruwe
            team-pagina met meer begrip.
          </div>
        )}

        {showAi && (
          <AiModal
            type="employees"
            companyIds={[company.id]}
            onClose={() => setShowAi(false)}
            onApplied={load}
          />
        )}
      </div>
    </div>
  )
}
