import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api, clearToken, downloadExport } from '../api'
import AiModal from '../components/AiModal'
import CompanyMap from '../components/CompanyMap'
import EmployeesModal from '../components/EmployeesModal'
import MailQueueModal from '../components/MailQueueModal'
import TemplateModal from '../components/TemplateModal'
import type { Company, Message, SearchDetail } from '../types'

export default function SearchView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [search, setSearch] = useState<SearchDetail | null>(null)
  const [error, setError] = useState('')
  const [view, setView] = useState<'list' | 'map'>('list')

  // filters
  const [category, setCategory] = useState('')
  const [gemeente, setGemeente] = useState('')
  const [onlyContacted, setOnlyContacted] = useState(false)
  const [onlyEmail, setOnlyEmail] = useState(false)

  // selection + modals
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [templateModal, setTemplateModal] = useState<'email' | 'linkedin' | null>(null)
  const [mailQueue, setMailQueue] = useState<Company[] | null>(null)
  const [employeesFor, setEmployeesFor] = useState<Company | null>(null)
  const [aiModal, setAiModal] = useState<'enrich' | 'email' | 'linkedin' | null>(null)
  const [exportOpen, setExportOpen] = useState(false)

  // enrichment progress
  const [enriching, setEnriching] = useState<{ done: number; total: number } | null>(null)

  const load = useCallback(async () => {
    try {
      setSearch(await api.get<SearchDetail>(`/api/searches/${id}`))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Laden mislukt')
    }
  }, [id])

  useEffect(() => {
    load()
  }, [load])

  const companies = search?.companies ?? []

  const categories = useMemo(
    () => [...new Set(companies.map((c) => c.category).filter(Boolean))] as string[],
    [companies],
  )
  const gemeentes = useMemo(
    () => [...new Set(companies.map((c) => c.gemeente).filter(Boolean))] as string[],
    [companies],
  )

  const filtered = useMemo(
    () =>
      companies.filter((c) => {
        if (category && c.category !== category) return false
        if (gemeente && c.gemeente !== gemeente) return false
        if (onlyContacted && !c.contacted) return false
        if (onlyEmail && !c.email) return false
        return true
      }),
    [companies, category, gemeente, onlyContacted, onlyEmail],
  )

  const mailable = filtered.filter((c) => c.email)
  const targetIds = selected.size > 0 ? [...selected] : filtered.map((c) => c.id)

  function toggleSelect(companyId: number) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(companyId)) next.delete(companyId)
      else next.add(companyId)
      return next
    })
  }

  async function enrichAll() {
    const targets = filtered.filter((c) => c.website && !c.enriched)
    if (targets.length === 0) return
    setEnriching({ done: 0, total: targets.length })
    for (let i = 0; i < targets.length; i++) {
      try {
        await api.post(`/api/companies/${targets[i].id}/enrich`)
      } catch {
        /* keep going */
      }
      setEnriching({ done: i + 1, total: targets.length })
    }
    setEnriching(null)
    load()
  }

  async function openMail(c: Company) {
    const message = await api.get<Message>(`/api/companies/${c.id}/message?kind=email`)
    if (message.mailto) {
      window.location.href = message.mailto
      await api.patch(`/api/companies/${c.id}`, { contacted: true })
      load()
    }
  }

  async function copyLinkedin(c: Company) {
    const message = await api.get<Message>(`/api/companies/${c.id}/message?kind=linkedin`)
    await navigator.clipboard.writeText(message.body)
    if (c.linkedin) window.open(c.linkedin, '_blank')
  }

  async function remove() {
    if (!search) return
    if (!confirm(`Zoekopdracht "${search.sector} in ${search.location}" verwijderen?`)) return
    await api.delete(`/api/searches/${search.id}`)
    navigate('/')
  }

  if (!search) {
    return (
      <div className="page">
        {error ? <div className="error-banner">{error}</div> : <div className="empty">Laden…</div>}
      </div>
    )
  }

  return (
    <div className="page">
      <div className="topbar">
        <button className="btn" onClick={() => navigate('/')}>
          ← Terug
        </button>
        <div>
          🏢 <b>{search.sector}</b> in <b>{search.location}</b>
          <div>
            <span className="credits-chip">⚡ {search.credits_used} credits</span>
          </div>
        </div>
        <div className="spacer" />
        <button className="btn" onClick={() => setTemplateModal('email')}>
          ✉️ E-mail Template
        </button>
        <button className="btn" onClick={() => setTemplateModal('linkedin')}>
          💼 LinkedIn Template
        </button>
        <div style={{ position: 'relative' }}>
          <button className="btn" onClick={() => setExportOpen((v) => !v)}>
            ⬇️ Exporteren ▾
          </button>
          {exportOpen && (
            <div
              className="card"
              style={{ position: 'absolute', top: '110%', right: 0, zIndex: 20, padding: 8, minWidth: 200 }}
            >
              {(
                [
                  ['csv', '📄 Exporteer CSV'],
                  ['xlsx', '📊 Exporteer Excel'],
                  ['hubspot', '🔗 Exporteer naar CRM (HubSpot)'],
                ] as const
              ).map(([format, label]) => (
                <button
                  key={format}
                  className="btn"
                  style={{ display: 'block', width: '100%', border: 'none', textAlign: 'left' }}
                  onClick={() => {
                    setExportOpen(false)
                    downloadExport(search.id, format)
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          )}
        </div>
        <button className="btn danger" onClick={remove}>
          🗑️ Verwijderen
        </button>
        <button className="btn primary" onClick={() => setMailQueue(mailable)} disabled={mailable.length === 0}>
          ✉️ Bereid {mailable.length} mails voor
        </button>
        <button
          className="btn"
          onClick={() => {
            clearToken()
            navigate('/login')
          }}
        >
          [→ Uitloggen
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="filterbar">
        <span className="muted">☰ Filters:</span>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">Alle categorieën</option>
          {categories.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
        <select value={gemeente} onChange={(e) => setGemeente(e.target.value)}>
          <option value="">Alle gemeentes</option>
          {gemeentes.map((g) => (
            <option key={g}>{g}</option>
          ))}
        </select>
        <button className={`btn pill small ${onlyContacted ? 'active' : ''}`} onClick={() => setOnlyContacted((v) => !v)}>
          ✓ Alleen gecontacteerd
        </button>
        <button className={`btn pill small ${onlyEmail ? 'active' : ''}`} onClick={() => setOnlyEmail((v) => !v)}>
          ✉️ Alleen e-mail
        </button>
        <button className="btn pill small" onClick={enrichAll} disabled={enriching !== null}>
          {enriching ? `Verrijken… ${enriching.done}/${enriching.total}` : '✨ Verrijken'}
        </button>
        <button className="btn pill small" onClick={() => setAiModal('enrich')}>
          ✨ AI via Claude
        </button>
        <button className="btn pill small" onClick={() => setAiModal('email')}>
          ✉️ AI-mails via Claude
        </button>
        <span className="count">
          {filtered.length} van {companies.length} bedrijven
        </span>
      </div>

      <div style={{ marginBottom: 12 }}>
        <button className={`btn small ${view === 'list' ? 'active' : ''}`} onClick={() => setView('list')}>
          ☰ Lijst
        </button>{' '}
        <button className={`btn small ${view === 'map' ? 'active' : ''}`} onClick={() => setView('map')}>
          🗺️ Kaart
        </button>
      </div>

      {view === 'map' ? (
        <CompanyMap companies={filtered} />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th className="checkbox-cell">✓</th>
                <th>Bedrijfsnaam</th>
                <th>Adres</th>
                <th>Gemeente</th>
                <th>Telefoon</th>
                <th>E-mail</th>
                <th>Website</th>
                <th>Categorie</th>
                <th>🕓</th>
                <th>📷</th>
                <th>f</th>
                <th>in</th>
                <th>Medewerkers</th>
                <th>Omschrijving</th>
                <th>BTW-nummer</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => (
                <tr key={c.id}>
                  <td className="checkbox-cell">
                    <input type="checkbox" checked={selected.has(c.id)} onChange={() => toggleSelect(c.id)} />
                  </td>
                  <td>
                    <b>{c.name}</b>
                    {c.zaakvoerder && <div className="muted" style={{ fontSize: 12 }}>👤 {c.zaakvoerder}</div>}
                  </td>
                  <td>{c.address ?? '-'}</td>
                  <td className="nowrap">{c.gemeente ?? '-'}</td>
                  <td className="nowrap">{c.phone ? <a href={`tel:${c.phone}`}>📞 {c.phone}</a> : '-'}</td>
                  <td className="nowrap">
                    {c.email ? (
                      <a
                        href="#mail"
                        onClick={(e) => {
                          e.preventDefault()
                          openMail(c)
                        }}
                        title="Opent gepersonaliseerde mail in je mail-app"
                      >
                        {c.email}
                      </a>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className="nowrap">
                    {c.website ? (
                      <a href={c.website} target="_blank" rel="noreferrer">
                        🔗 Bezoek
                      </a>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td>{c.category ? <span className="tag">🏷️ {c.category}</span> : '-'}</td>
                  <td title={c.contacted_at ? `Gecontacteerd op ${new Date(c.contacted_at).toLocaleString('nl-BE')}` : ''}>
                    {c.contacted ? '🕓' : '-'}
                  </td>
                  <td>
                    {c.instagram ? (
                      <a href={c.instagram} target="_blank" rel="noreferrer">
                        📷
                      </a>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td>
                    {c.facebook ? (
                      <a href={c.facebook} target="_blank" rel="noreferrer">
                        f
                      </a>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td>
                    {c.linkedin ? (
                      <a
                        href="#li"
                        onClick={(e) => {
                          e.preventDefault()
                          copyLinkedin(c)
                        }}
                        title="Kopieert gepersonaliseerd bericht en opent LinkedIn"
                      >
                        in
                      </a>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className="nowrap">
                    <button className="btn small" onClick={() => setEmployeesFor(c)}>
                      👥 Vind medewerkers
                    </button>
                  </td>
                  <td>{c.description ? <div className="desc" title={c.description}>📄 {c.description}</div> : '-'}</td>
                  <td className="nowrap">
                    {c.vat ? (
                      <span className="mono">{c.vat}</span>
                    ) : (
                      <a
                        href={`https://kbopub.economie.fgov.be/kbopub/zoeknaamfonetischform.html?searchWord=${encodeURIComponent(c.name)}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        🌐 Zoek
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && <div className="empty">Geen bedrijven in deze selectie</div>}
        </div>
      )}

      {templateModal && <TemplateModal kind={templateModal} onClose={() => setTemplateModal(null)} />}
      {mailQueue && (
        <MailQueueModal
          companies={mailQueue}
          onContacted={() => load()}
          onClose={() => {
            setMailQueue(null)
            load()
          }}
        />
      )}
      {employeesFor && <EmployeesModal company={employeesFor} onClose={() => setEmployeesFor(null)} />}
      {aiModal && (
        <AiModal
          type={aiModal}
          companyIds={targetIds}
          onClose={() => setAiModal(null)}
          onApplied={load}
        />
      )}
    </div>
  )
}
