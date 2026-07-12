import L from 'leaflet'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'
import type { Company } from '../types'

// Leaflet's default marker images don't resolve under Vite; bundle them explicitly.
const icon = L.icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

export default function CompanyMap({ companies }: { companies: Company[] }) {
  const located = companies.filter((c) => c.lat != null && c.lon != null)
  if (located.length === 0) {
    return <div className="empty">Geen bedrijven met coördinaten in deze selectie</div>
  }
  const avgLat = located.reduce((s, c) => s + (c.lat as number), 0) / located.length
  const avgLon = located.reduce((s, c) => s + (c.lon as number), 0) / located.length

  return (
    <div className="map-container">
      <MapContainer center={[avgLat, avgLon]} zoom={12} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {located.map((c) => (
          <Marker key={c.id} position={[c.lat as number, c.lon as number]} icon={icon}>
            <Popup>
              <div className="map-popup">
                <b>{c.name}</b>
                <br />
                {c.address && (
                  <>
                    {c.address}
                    <br />
                  </>
                )}
                {c.phone && (
                  <>
                    <a href={`tel:${c.phone}`}>{c.phone}</a>
                    <br />
                  </>
                )}
                {c.website && (
                  <>
                    <a href={c.website} target="_blank" rel="noreferrer">
                      Website →
                    </a>
                    <br />
                  </>
                )}
                {c.category && <span className="tag">{c.category}</span>}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}
