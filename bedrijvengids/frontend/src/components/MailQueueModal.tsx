import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Company, Message } from '../types'

interface Props {
  companies: Company[]
  onContacted: (companyId: number) => void
  onClose: () => void
}

interface Item {
  company: Company
  message: Message | null
  opened: boolean
}

export default function MailQueueModal({ companies, onContacted, onClose }: Props) {
  const [items, setItems] = useState<Item[]>(
    companies.map((c) => ({ company: c, message: null, opened: false })),
  )
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load() {
      const loaded: Item[] = []
      for (const c of companies) {
        try {
          const message = await api.get<Message>(`/api/companies/${c.id}/message?kind=email`)
          loaded.push({ company: c, message, opened: false })
        } catch {
          loaded.push({ company: c, message: null, opened: false })
        }
      }
      if (!cancelled) {
        setItems(loaded)
        setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [companies])

  async function open(index: number) {
    const item = items[index]
    if (!item.message?.mailto) return
    window.location.href = item.message.mailto
    setItems((prev) => prev.map((it, i) => (i === index ? { ...it, opened: true } : it)))
    try {
      await api.patch(`/api/companies/${item.company.id}`, { contacted: true })
      onContacted(item.company.id)
    } catch {
      /* non-fatal */
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h2>✉️ Bereid {companies.length} mails voor</h2>
          <button className="modal-close" onClick={onClose}>
            ✕
          </button>
        </div>
        <div className="section-sub">
          Elke mail opent in je eigen e-mailprogramma met ontvanger, onderwerp en inhoud vooraf ingevuld. Jij
          controleert en verstuurt. Geopende prospects worden als gecontacteerd gemarkeerd.
        </div>
        {loading && <div className="empty">Berichten personaliseren…</div>}
        {!loading &&
          items.map((item, i) => (
            <div className="mail-item" key={item.company.id}>
              <div className="mail-head">
                <b>{item.company.name}</b>
                {item.message?.source === 'ai' && <span className="ai-chip">AI-gepersonaliseerd</span>}
                <span className="muted">{item.company.email}</span>
                <button className="btn small primary" onClick={() => open(i)} disabled={!item.message?.mailto}>
                  {item.opened ? '✓ Geopend' : '✉️ Open in mail-app'}
                </button>
              </div>
              {item.message && (
                <div className="mail-preview">
                  <b>{item.message.subject}</b>
                  {'\n'}
                  {item.message.body}
                </div>
              )}
            </div>
          ))}
        <div className="modal-actions">
          <button className="btn" onClick={onClose}>
            Sluiten
          </button>
        </div>
      </div>
    </div>
  )
}
