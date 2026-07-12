"""Mapping of Dutch sector keywords to OpenStreetMap tag filters.

Each entry maps a set of keywords to a list of (key, value) OSM tags and a
human-readable Dutch category label. Unknown sectors fall back to a
name/description regex search in Overpass.
"""

SECTOR_MAP: list[dict] = [
    {"keywords": ["bakker", "bakkerij"], "tags": [("shop", "bakery")], "label": "Bakkerij"},
    {"keywords": ["kapper", "kapsalon", "barbier"], "tags": [("shop", "hairdresser")], "label": "Kapper"},
    {"keywords": ["slager", "slagerij"], "tags": [("shop", "butcher")], "label": "Slagerij"},
    {
        "keywords": ["vastgoed", "vastgoedmakelaar", "immo", "immokantoor", "makelaar"],
        "tags": [("office", "estate_agent")],
        "label": "Vastgoedmakelaar",
    },
    {
        "keywords": ["bouwbedrijf", "bouw", "aannemer", "bouwonderneming"],
        "tags": [
            ("office", "construction_company"),
            ("craft", "builder"),
            ("industrial", "construction"),
            ("craft", "mason"),
        ],
        "label": "Bouwbedrijf",
    },
    {"keywords": ["advocaat", "advocatenkantoor"], "tags": [("office", "lawyer")], "label": "Advocaat"},
    {
        "keywords": ["boekhouder", "accountant", "boekhoudkantoor", "fiscaal"],
        "tags": [("office", "accountant")],
        "label": "Boekhouder",
    },
    {"keywords": ["notaris"], "tags": [("office", "notary")], "label": "Notaris"},
    {"keywords": ["restaurant"], "tags": [("amenity", "restaurant")], "label": "Restaurant"},
    {
        "keywords": ["cafe", "café", "bar", "kroeg"],
        "tags": [("amenity", "cafe"), ("amenity", "bar"), ("amenity", "pub")],
        "label": "Café",
    },
    {"keywords": ["frituur", "frietkot"], "tags": [("amenity", "fast_food")], "label": "Frituur"},
    {
        "keywords": ["garage", "autogarage", "carrosserie"],
        "tags": [("shop", "car_repair")],
        "label": "Garage",
    },
    {"keywords": ["autodealer", "autohandel"], "tags": [("shop", "car")], "label": "Autodealer"},
    {"keywords": ["apotheek", "apotheker"], "tags": [("amenity", "pharmacy")], "label": "Apotheek"},
    {"keywords": ["tandarts", "tandartspraktijk"], "tags": [("amenity", "dentist")], "label": "Tandarts"},
    {
        "keywords": ["dokter", "huisarts", "arts"],
        "tags": [("amenity", "doctors")],
        "label": "Huisarts",
    },
    {"keywords": ["dierenarts"], "tags": [("amenity", "veterinary")], "label": "Dierenarts"},
    {
        "keywords": ["kinesist", "kinesitherapeut", "fysiotherapeut"],
        "tags": [("healthcare", "physiotherapist")],
        "label": "Kinesist",
    },
    {
        "keywords": ["fitness", "sportschool", "gym"],
        "tags": [("leisure", "fitness_centre")],
        "label": "Fitness",
    },
    {"keywords": ["hotel"], "tags": [("tourism", "hotel")], "label": "Hotel"},
    {"keywords": ["b&b", "bed and breakfast"], "tags": [("tourism", "guest_house")], "label": "B&B"},
    {
        "keywords": ["schilder", "schildersbedrijf"],
        "tags": [("craft", "painter")],
        "label": "Schildersbedrijf",
    },
    {"keywords": ["elektricien", "elektriciteitswerken"], "tags": [("craft", "electrician")], "label": "Elektricien"},
    {
        "keywords": ["loodgieter", "sanitair", "verwarming", "chauffagist"],
        "tags": [("craft", "plumber"), ("craft", "hvac")],
        "label": "Loodgieter",
    },
    {
        "keywords": ["tuinaanleg", "tuinarchitect", "tuinman", "tuinonderhoud"],
        "tags": [("craft", "gardener")],
        "label": "Tuinaanleg",
    },
    {"keywords": ["dakwerker", "dakwerken"], "tags": [("craft", "roofer")], "label": "Dakwerker"},
    {
        "keywords": ["schrijnwerker", "schrijnwerkerij", "houtbewerking", "meubelmaker"],
        "tags": [("craft", "carpenter"), ("craft", "joiner")],
        "label": "Schrijnwerker",
    },
    {
        "keywords": ["verzekeringen", "verzekeringsmakelaar", "verzekeringskantoor"],
        "tags": [("office", "insurance")],
        "label": "Verzekeringen",
    },
    {"keywords": ["bank", "bankkantoor"], "tags": [("amenity", "bank")], "label": "Bank"},
    {"keywords": ["opticien", "optiek", "brillenwinkel"], "tags": [("shop", "optician")], "label": "Opticien"},
    {"keywords": ["juwelier"], "tags": [("shop", "jewelry")], "label": "Juwelier"},
    {"keywords": ["bloemist", "bloemenwinkel"], "tags": [("shop", "florist")], "label": "Bloemist"},
    {"keywords": ["fietsenwinkel", "fietsenmaker", "fietshandel"], "tags": [("shop", "bicycle")], "label": "Fietsenwinkel"},
    {
        "keywords": ["it", "webdesign", "software", "informatica", "webbureau"],
        "tags": [("office", "it")],
        "label": "IT-bedrijf",
    },
    {
        "keywords": ["marketing", "reclamebureau", "communicatiebureau", "marketingbureau"],
        "tags": [("office", "advertising_agency"), ("office", "marketing")],
        "label": "Marketingbureau",
    },
    {
        "keywords": ["architect", "architectenbureau"],
        "tags": [("office", "architect")],
        "label": "Architect",
    },
    {"keywords": ["drukkerij", "drukker"], "tags": [("shop", "printing"), ("craft", "printer")], "label": "Drukkerij"},
    {"keywords": ["schoonmaakbedrijf", "poetsbedrijf", "poetsdienst"], "tags": [("craft", "cleaning")], "label": "Schoonmaakbedrijf"},
    {"keywords": ["kinderopvang", "kinderdagverblijf", "creche", "crèche"], "tags": [("amenity", "childcare"), ("amenity", "kindergarten")], "label": "Kinderopvang"},
    {"keywords": ["rijschool"], "tags": [("amenity", "driving_school")], "label": "Rijschool"},
    {"keywords": ["reisbureau"], "tags": [("shop", "travel_agency")], "label": "Reisbureau"},
    {"keywords": ["wasserij", "droogkuis"], "tags": [("shop", "laundry"), ("shop", "dry_cleaning")], "label": "Wasserij"},
    {"keywords": ["brouwerij"], "tags": [("craft", "brewery")], "label": "Brouwerij"},
    {"keywords": ["supermarkt", "kruidenier"], "tags": [("shop", "supermarket"), ("shop", "convenience")], "label": "Supermarkt"},
    {"keywords": ["kledingwinkel", "boetiek", "kleding"], "tags": [("shop", "clothes")], "label": "Kledingwinkel"},
    {"keywords": ["schoenwinkel", "schoenen"], "tags": [("shop", "shoes")], "label": "Schoenwinkel"},
    {"keywords": ["boekhandel", "boekenwinkel"], "tags": [("shop", "books")], "label": "Boekhandel"},
]


def resolve_sector(sector: str) -> tuple[list[tuple[str, str]], str, bool]:
    """Return (osm tag filters, Dutch category label, matched).

    When no keyword matches, returns an empty tag list and matched=False so the
    caller can fall back to a free-text Overpass name search.
    """
    needle = sector.strip().lower()
    for entry in SECTOR_MAP:
        for kw in entry["keywords"]:
            if kw in needle or needle in kw:
                return entry["tags"], entry["label"], True
    return [], sector.strip().capitalize(), False
