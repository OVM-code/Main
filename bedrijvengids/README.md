# Bedrijvengids.AI

AI-gedreven B2B-leadprospectie voor KMO's — zoek bedrijven per **sector en locatie**, breng ze **in kaart**, **verrijk** ze met contactgegevens en bedrijfsinfo, en bereid **gepersonaliseerde outreach** voor. Minder research, meer gesprekken.

Gebouwd naar het concept uit de AI-D pitch deck:

| Slide-feature | Implementatie |
| --- | --- |
| Gericht zoeken op sector en locatie | Dashboard met zoekopdrachten, totaal bedrijven, maandelijks verbruik (40.000 credits) en zoekgeschiedenis |
| Live scraping | OpenStreetMap (Nominatim + Overpass) vindt bedrijven; daarna wordt elke bedrijfswebsite gescraped voor e-mail, telefoon, BTW-nummer, socials, omschrijving en zaakvoerder |
| Lijst van potentiële leads | Tabel met adres, gemeente, telefoon, e-mail, website, categorie, gecontacteerd-status, Instagram/Facebook/LinkedIn, omschrijving, BTW-nummer (met KBO-zoeklink) |
| Breng prospects in kaart | Leaflet-kaartweergave met popups |
| Verrijk je lijst met AI | Regelgebaseerde verrijking + "AI via Claude"-flow (zie hieronder) |
| Persoonlijke outreach via AI | E-mail- en LinkedIn-templates met `{bedrijfsnaam}` / `{zaakvoerder}` / `{gemeente}` placeholders, basis- of AI-personalisatie, "Bereid X mails voor" opent je eigen mail-app |
| Vind medewerkers (multithreading sales) | Team-pagina's scrapen per bedrijf → naam, functie, niveau (C-Level / Directeur / Manager / Medewerker) |
| Zoeken op personen | Doorzoek alle gevonden medewerkers op functie, sector, locatie en niveau |
| Export en CRM-koppeling | CSV, Excel, en HubSpot-import-CSV |

## AI zonder API-kosten: jouw Claude-abonnement

Deze app roept **geen betaalde LLM-API's** aan. AI-features werken via een copy-paste-flow met je bestaande Claude-abonnement:

1. Klik **"AI via Claude"** (verrijking), **"AI-mails via Claude"** (personalisatie) of **"Betere extractie via Claude"** (medewerkers).
2. De app genereert een kant-en-klare prompt met alle bedrijfsdata (inclusief gescrapete websitetekst).
3. Plak de prompt in [claude.ai](https://claude.ai) of Claude Code.
4. Plak Claude's JSON-antwoord terug in de app → resultaten worden toegepast op de database.

Zelfde resultaat als een API-integratie, nul variabele kosten.

## Snel starten

Vereisten: Python 3.11+ en Node 20+.

```bash
# Backend
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --port 8000

# Frontend (tweede terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — standaard wachtwoord: `demo`.

Demo-data laden zonder netwerk (bouwbedrijf in Hasselt, zoals in de deck):

```bash
cd backend && .venv/bin/python seed_demo.py
```

## Configuratie (omgevingsvariabelen)

| Variabele | Standaard | Betekenis |
| --- | --- | --- |
| `BG_PASSWORD` | `demo` | Login-wachtwoord |
| `BG_SECRET` | dev-waarde | Token-signing secret — zet in productie |
| `BG_CREDIT_LIMIT` | `40000` | Maandelijkse creditlimiet (reset op de 1e) |
| `BG_DATA_DIR` | `backend/data` | Locatie van de SQLite-database |

Creditmodel: 5 credits per gevonden bedrijf, 2 per verrijking, 2 per medewerker-zoekopdracht.

## Architectuur

```
bedrijvengids/
├── backend/            FastAPI + SQLAlchemy + SQLite
│   ├── app/
│   │   ├── main.py             alle API-routes, auth, credits
│   │   ├── models.py           Search, Company, Employee, Template, UsageEvent
│   │   └── services/
│   │       ├── sectors.py      Nederlandse sectortermen → OSM-tags (45+ sectoren)
│   │       ├── osm.py          Nominatim-geocoding + Overpass-queries
│   │       ├── scraper.py      website-scraping: e-mail, BTW, zaakvoerder, team
│   │       ├── personalize.py  template-rendering + mailto-links
│   │       ├── prompts.py      Claude-promptgeneratie + JSON-verwerking
│   │       └── exports.py      CSV / Excel / HubSpot
│   ├── seed_demo.py    demo-data (offline demo's)
│   └── tests/          13 tests, geen netwerk nodig: pytest tests/
└── frontend/           React + TypeScript + Vite + Leaflet
    └── src/
        ├── pages/      Dashboard, SearchView (lijst/kaart), PeopleSearch, Login
        └── components/ CompanyMap, TemplateModal, MailQueueModal,
                        EmployeesModal, AiModal (Claude-flow)
```

### Databronnen

- **Nominatim** geocodeert de locatie naar een gemeente-/provinciegrens.
- **Overpass** zoekt bedrijven binnen dat gebied op OSM-tags (bv. `office=estate_agent` voor "vastgoedmakelaar"). Onbekende sectoren vallen terug op vrije-tekst-matching.
- **Website-scraping** (alleen de eigen site van elk bedrijf): mailto-links, BTW-regex (`BE0xxx.xxx.xxx`), telefoon-regex, social-links, meta-description, zaakvoerder-detectie en team-pagina's.

Let op: respecteer de [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/) en scrape verantwoord (de app bezoekt per bedrijf enkele pagina's van de eigen website, éénmalig per verrijking).

## Beperkingen t.o.v. de pitch deck

- **Personen-zoeken** werkt op medewerkers die van bedrijfswebsites gescrapet zijn — er is geen externe personendatabase (zoals Apollo/LinkedIn-data in commerciële tools). Filters op #VTE/omzet uit de deck vereisen zo'n databron.
- **HubSpot-koppeling** is een import-klare CSV, geen live API-sync.
- **Companyweb-integratie** is vervangen door een KBO-zoeklink per bedrijf.
