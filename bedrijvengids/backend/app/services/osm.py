"""Company discovery via OpenStreetMap: Nominatim geocoding + Overpass queries."""

import logging
import re

import httpx

from .sectors import resolve_sector

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
USER_AGENT = "Bedrijvengids.AI-clone/1.0 (lead prospecting demo)"


class OsmError(Exception):
    pass


def geocode_area(location: str, country: str) -> dict:
    """Geocode a municipality/province to an Overpass area id (or bbox fallback)."""
    query = f"{location}, {country}" if country else location
    resp = httpx.get(
        NOMINATIM_URL,
        params={"q": query, "format": "json", "limit": 5, "addressdetails": 1},
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise OsmError(f"Locatie '{location}' niet gevonden")

    # Prefer administrative boundaries (municipalities, provinces) over POIs.
    def rank(r: dict) -> int:
        score = 0
        if r.get("osm_type") == "relation":
            score += 2
        if r.get("class") == "boundary" or r.get("type") in ("administrative", "city", "town", "village"):
            score += 3
        return score

    best = max(results, key=rank)
    area: dict = {"display_name": best.get("display_name", location)}
    if best.get("osm_type") == "relation":
        area["area_id"] = 3600000000 + int(best["osm_id"])
    elif best.get("osm_type") == "way":
        area["area_id"] = 2400000000 + int(best["osm_id"])
    if "boundingbox" in best:
        s, n, w, e = (float(x) for x in best["boundingbox"])
        area["bbox"] = (s, w, n, e)
    if not area.get("area_id") and not area.get("bbox"):
        raise OsmError(f"Geen bruikbaar zoekgebied voor '{location}'")
    return area


def _overpass_query(area: dict, tag_filters: list[tuple[str, str]], name_regex: str | None) -> str:
    if area.get("area_id"):
        scope = f"area(id:{area['area_id']})->.a;"
        suffix = "(area.a)"
    else:
        s, w, n, e = area["bbox"]
        scope = ""
        suffix = f"({s},{w},{n},{e})"

    clauses = []
    for key, value in tag_filters:
        clauses.append(f'nwr["{key}"="{value}"]{suffix};')
    if name_regex:
        safe = re.sub(r'["\\\\]', "", name_regex)
        # Free-text fallback: match the sector term in the name or business tag
        # of anything that looks like a business (has a shop/craft/office/... tag).
        for key in ("shop", "craft", "office", "amenity", "tourism", "leisure", "healthcare"):
            clauses.append(f'nwr["{key}"]["name"~"{safe}",i]{suffix};')
            clauses.append(f'nwr["{key}"~"{safe}",i]{suffix};')

    body = "\n  ".join(clauses)
    return f"""[out:json][timeout:90];
{scope}
(
  {body}
);
out center tags 500;
"""


def _first_tag(tags: dict, *keys: str) -> str | None:
    for key in keys:
        if tags.get(key):
            return tags[key]
    return None


def _build_address(tags: dict) -> tuple[str | None, str | None]:
    street = tags.get("addr:street")
    number = tags.get("addr:housenumber")
    postcode = tags.get("addr:postcode")
    city = tags.get("addr:city")
    parts = []
    if street:
        parts.append(f"{street} {number}".strip() if number else street)
    tail = " ".join(p for p in (postcode, city) if p)
    if tail:
        parts.append(tail)
    address = ", ".join(parts) if parts else None
    return address, city


def _category_label(tags: dict, default_label: str) -> str:
    # Reverse-map a handful of common tags to Dutch labels; fall back to the
    # sector the user typed.
    from .sectors import SECTOR_MAP

    for entry in SECTOR_MAP:
        for key, value in entry["tags"]:
            if tags.get(key) == value:
                return entry["label"]
    return default_label


def search_companies(sector: str, location: str, country: str) -> list[dict]:
    """Find companies for a sector in a location. Returns normalized dicts."""
    tag_filters, label, matched = resolve_sector(sector)
    area = geocode_area(location, country or "België")
    name_regex = None if matched else sector.strip()
    query = _overpass_query(area, tag_filters, name_regex)

    last_error: Exception | None = None
    elements: list[dict] = []
    for url in OVERPASS_URLS:
        try:
            resp = httpx.post(url, data={"data": query}, headers={"User-Agent": USER_AGENT}, timeout=120)
            resp.raise_for_status()
            elements = resp.json().get("elements", [])
            break
        except Exception as exc:  # noqa: BLE001 - try the next mirror
            last_error = exc
            logger.warning("Overpass mirror %s failed: %s", url, exc)
    else:
        raise OsmError(f"Overpass niet bereikbaar: {last_error}")

    companies: list[dict] = []
    seen_names: set[str] = set()
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
        dedup_key = name.strip().lower()
        if dedup_key in seen_names:
            continue
        seen_names.add(dedup_key)

        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        address, city = _build_address(tags)
        website = _first_tag(tags, "website", "contact:website", "url")
        if website and not website.startswith("http"):
            website = "https://" + website

        companies.append(
            {
                "osm_ref": f"{el.get('type', 'n')[0]}{el.get('id')}",
                "name": name,
                "address": address,
                "gemeente": city,
                "phone": _first_tag(tags, "phone", "contact:phone", "contact:mobile"),
                "email": _first_tag(tags, "email", "contact:email"),
                "website": website,
                "category": _category_label(tags, label),
                "lat": lat,
                "lon": lon,
                "facebook": _first_tag(tags, "contact:facebook"),
                "instagram": _first_tag(tags, "contact:instagram"),
                "linkedin": _first_tag(tags, "contact:linkedin"),
                "description": tags.get("description"),
                "zaakvoerder": tags.get("operator"),
            }
        )
    return companies
