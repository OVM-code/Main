import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import type { Person } from '../types'

function levelClass(level: string | null): string {
  if (level === 'C-Level') return 'level-badge c-level'
  if (level === 'Directeur') return 'level-badge directeur'
  return 'level-badge'
}

export default function PeopleSearch() {
  const [functie, setFunctie] = useState('')
  const [locatie, setLocatie] = useState('')
  const [sector, setSector] = useState('')
  const [level, setLevel] = useState('')
  const [people, setPeople] = useState<Person[]>([])
  const [loaded, setLoaded] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function load() {
    setError('')
    try {
      const params = new URLSearchParams()
      if (functie) params.set('functie', functie)
      if (locatie) params.set('locatie', locatie)
      if (sector) params.set('sector', sector)
      if (level) params.set('level', level)
      setPeople(await api.get<Person[]>(`/api/people?${params}`))
      setLoaded(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Zoeken mislukt')
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="page">
      <div className="topbar">
        <button className="btn" onClick={() => navigate('/')}>
          ← Terug
        </button>
        <div className="brand">
          👥 Zoeken op <span>personen</span>
        </div>
        <div className="spacer" />
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="section-sub">
          Doorzoek alle gevonden medewerkers over je zoekopdrachten heen. Tip: gebruik "Vind medewerkers" in een
          bedrijvenlijst om deze database te vullen — functie + sector + regio + filters → gestructureerde
          kandidaten- of contactenlijst.
        </div>
        <div className="form-row">
          <label className="field">
            Functie
            <input value={functie} onChange={(e) => setFunctie(e.target.value)} placeholder="bijv. CTO, Office Manager" />
          </label>
          <label className="field">
            Sector
            <input value={sector} onChange={(e) => setSector(e.target.value)} placeholder="bijv. Bouwbedrijf" />
          </label>
          <label className="field">
            Locatie
            <input value={locatie} onChange={(e) => setLocatie(e.target.value)} placeholder="bijv. Hasselt" />
          </label>
          <label className="field">
            Niveau
            <select value={level} onChange={(e) => setLevel(e.target.value)}>
              <option value="">Alle niveaus</option>
              <option>C-Level</option>
              <option>Directeur</option>
              <option>Manager</option>
              <option>Medewerker</option>
            </select>
          </label>
        </div>
        <button className="btn primary" onClick={load}>
          🔍 Zoeken
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="filterbar">
        <span className="count">{people.length} personen</span>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Naam</th>
              <th>Functie</th>
              <th>Niveau</th>
              <th>E-mail</th>
              <th>Telefoon</th>
              <th>LinkedIn</th>
              <th>Bedrijf</th>
              <th>Sector</th>
              <th>Gemeente</th>
            </tr>
          </thead>
          <tbody>
            {people.map((p) => (
              <tr key={p.id}>
                <td>
                  <b>{p.name}</b>
                </td>
                <td>{p.role ?? '-'}</td>
                <td>{p.level ? <span className={levelClass(p.level)}>{p.level}</span> : '-'}</td>
                <td className="nowrap">{p.email ? <a href={`mailto:${p.email}`}>{p.email}</a> : '-'}</td>
                <td className="nowrap">{p.phone ?? '-'}</td>
                <td>
                  {p.linkedin ? (
                    <a href={p.linkedin} target="_blank" rel="noreferrer">
                      💼 Profiel
                    </a>
                  ) : (
                    <a
                      href={`https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(`${p.name} ${p.company_name}`)}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      🔍 Zoek
                    </a>
                  )}
                </td>
                <td>
                  {p.website ? (
                    <a href={p.website} target="_blank" rel="noreferrer">
                      🏢 {p.company_name}
                    </a>
                  ) : (
                    <>🏢 {p.company_name}</>
                  )}
                </td>
                <td>{p.sector ? <span className="tag">{p.sector}</span> : '-'}</td>
                <td className="nowrap">{p.gemeente ?? '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {loaded && people.length === 0 && (
          <div className="empty">
            Nog geen personen gevonden. Open een zoekopdracht en gebruik "👥 Vind medewerkers" bij een bedrijf om
            personen toe te voegen.
          </div>
        )}
      </div>
    </div>
  )
}
