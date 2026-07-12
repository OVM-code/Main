"""Rule-based website scraping: contact details, VAT, socials, description,
owner detection and best-effort employee extraction. No LLM calls — pages that
resist rule-based extraction can be handed to Claude via the prompts service.
"""

import logging
import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36"
)

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+32|0032|0)\s?(?:\(0\))?\s?[1-9](?:[\s./-]?\d{2}){3,4}")
VAT_RE = re.compile(
    r"(?:BTW|TVA|VAT|Ondernemingsnummer|KBO)?\s*:?\s*(BE\s?0?\d{3}[.\s]?\d{3}[.\s]?\d{3})",
    re.IGNORECASE,
)
VAT_BARE_RE = re.compile(r"\b(0\d{3}[.\s]\d{3}[.\s]\d{3})\b")

# Case-insensitivity is scoped to the keywords only — the name pattern must
# keep its capitalization requirement or it matches arbitrary lowercase words.
OWNER_KEYWORDS = r"(?i:zaakvoerder|zaakvoerster|eigenaar|eigenares|oprichter|oprichtster|founder|CEO|bedrijfsleider|gérant|managing director)"
NAME_PATTERN = r"([A-Z][a-zà-ÿ]+(?:\s+(?:[Vv]an|[Dd]e[nr]?|[Tt]e[nr]?))*(?:\s+[A-Z][a-zà-ÿ]+){1,2})"
OWNER_BEFORE_RE = re.compile(NAME_PATTERN + r"\s*[,–—-]?\s*" + OWNER_KEYWORDS)
OWNER_AFTER_RE = re.compile(OWNER_KEYWORDS + r"\s*[:,–—-]?\s*(?:[a-zà-ÿ]+\s+){0,2}" + NAME_PATTERN)

CONTACT_PATHS = ["", "/contact", "/contacteer-ons", "/over-ons", "/about", "/info"]
TEAM_PATHS = ["/team", "/ons-team", "/over-ons", "/medewerkers", "/about", "/wie-zijn-we", "/mensen", "/people"]

ROLE_KEYWORDS = [
    "zaakvoerder", "ceo", "coo", "cfo", "cto", "founder", "oprichter", "partner",
    "director", "directeur", "directrice", "manager", "verantwoordelijke", "hoofd",
    "consultant", "adviseur", "account", "sales", "marketing", "hr", "office",
    "project", "engineer", "ingenieur", "architect", "ontwerper", "developer",
    "boekhouder", "administratie", "assistent", "medewerker", "expert", "specialist",
]


def _fetch(url: str, timeout: float = 15.0) -> str | None:
    try:
        resp = httpx.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "nl-BE,nl;q=0.9,en;q=0.5"},
            timeout=timeout,
            follow_redirects=True,
        )
        if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", "text/html"):
            return resp.text
    except Exception as exc:  # noqa: BLE001
        logger.debug("fetch %s failed: %s", url, exc)
    return None


def _clean_email(email: str) -> str | None:
    email = email.strip().strip(".,;:")
    lowered = email.lower()
    if any(bad in lowered for bad in ("example.", "sentry.", "@2x", ".png", ".jpg", ".webp", "wixpress")):
        return None
    return email


def _pick_email(emails: list[str], website: str) -> str | None:
    """Prefer info@/contact@ addresses on the company's own domain."""
    cleaned = [e for e in (_clean_email(e) for e in emails) if e]
    if not cleaned:
        return None
    domain = urlparse(website).netloc.removeprefix("www.")
    own = [e for e in cleaned if domain and e.lower().endswith("@" + domain)]
    pool = own or cleaned
    for prefix in ("info@", "contact@", "hello@", "hallo@", "welkom@", "office@", "admin@"):
        for e in pool:
            if e.lower().startswith(prefix):
                return e
    return pool[0]


def _extract_socials(soup: BeautifulSoup) -> dict:
    socials: dict[str, str | None] = {"facebook": None, "instagram": None, "linkedin": None}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        low = href.lower()
        if "facebook.com" in low and not socials["facebook"] and "sharer" not in low and "share.php" not in low:
            socials["facebook"] = href
        elif "instagram.com" in low and not socials["instagram"]:
            socials["instagram"] = href
        elif "linkedin.com" in low and not socials["linkedin"] and "share" not in low:
            socials["linkedin"] = href
    return socials


def _extract_description(soup: BeautifulSoup) -> str | None:
    for selector in (
        {"name": "meta", "attrs": {"name": "description"}},
        {"name": "meta", "attrs": {"property": "og:description"}},
    ):
        tag = soup.find(**selector)
        if tag and tag.get("content") and len(tag["content"].strip()) > 30:
            return tag["content"].strip()[:600]
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if len(text) > 80:
            return text[:600]
    return None


def _extract_owner(text: str) -> str | None:
    m = OWNER_AFTER_RE.search(text) or OWNER_BEFORE_RE.search(text)
    if m:
        name = m.group(1).strip()
        if 4 <= len(name) <= 60:
            return name
    return None


def _extract_vat(text: str) -> str | None:
    m = VAT_RE.search(text)
    if m:
        digits = re.sub(r"[^\d]", "", m.group(1))
        if len(digits) == 9:
            digits = "0" + digits
        if len(digits) == 10:
            return f"BE{digits[0]}{digits[1:4]}.{digits[4:7]}.{digits[7:10]}"
    m = VAT_BARE_RE.search(text)
    if m:
        digits = re.sub(r"[^\d]", "", m.group(1))
        if len(digits) == 10:
            return f"BE{digits[0]}{digits[1:4]}.{digits[4:7]}.{digits[7:10]}"
    return None


def enrich_from_website(website: str) -> dict:
    """Scrape a company website for contact data. Returns partial updates only."""
    result: dict = {"pages_text": ""}
    base = website if website.startswith("http") else "https://" + website

    emails: list[str] = []
    texts: list[str] = []
    soup_home: BeautifulSoup | None = None

    for path in CONTACT_PATHS:
        url = urljoin(base, path) if path else base
        html = _fetch(url)
        if not html:
            continue
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        if soup_home is None:
            soup_home = soup

        # mailto: links are the most reliable email source
        for a in soup.find_all("a", href=True):
            if a["href"].lower().startswith("mailto:"):
                emails.append(a["href"][7:].split("?")[0])
        text = soup.get_text(" ", strip=True)
        texts.append(text)
        emails.extend(EMAIL_RE.findall(text))

        socials = _extract_socials(soup)
        for key, value in socials.items():
            if value and not result.get(key):
                result[key] = value

        if not result.get("description"):
            desc = _extract_description(soup)
            if desc:
                result["description"] = desc

        if path == "" and not result.get("phone"):
            m = PHONE_RE.search(text)
            if m:
                result["phone"] = m.group(0).strip()

    full_text = "\n".join(texts)
    result["pages_text"] = full_text[:8000]

    if emails:
        email = _pick_email(emails, base)
        if email:
            result["email"] = email
    vat = _extract_vat(full_text)
    if vat:
        result["vat"] = vat
    owner = _extract_owner(full_text)
    if owner:
        result["zaakvoerder"] = owner
    if not result.get("phone"):
        m = PHONE_RE.search(full_text)
        if m:
            result["phone"] = m.group(0).strip()

    return result


def _level_for_role(role: str) -> str:
    low = role.lower()
    if any(k in low for k in ("ceo", "cfo", "coo", "cto", "zaakvoerder", "founder", "oprichter", "bedrijfsleider")):
        return "C-Level"
    if any(k in low for k in ("directeur", "director", "directrice", "partner")):
        return "Directeur"
    if any(k in low for k in ("manager", "verantwoordelijke", "hoofd", "lead")):
        return "Manager"
    return "Medewerker"


def find_employees(website: str) -> tuple[list[dict], str]:
    """Best-effort extraction of (name, role) pairs from team/about pages.

    Returns (employees, team_page_text) — the raw text lets the Claude prompt
    flow do a smarter pass on the same content.
    """
    base = website if website.startswith("http") else "https://" + website
    employees: list[dict] = []
    seen: set[str] = set()
    collected_text: list[str] = []

    name_re = re.compile(r"^[A-Z][a-zà-ÿ]+(?:\s+(?:[vV]an|[dD]e[nr]?|[tT]e[nr]?))*(?:\s+[A-Z][a-zà-ÿ]+){1,2}$")

    for path in TEAM_PATHS:
        url = urljoin(base, path)
        html = _fetch(url)
        if not html:
            continue
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text("\n", strip=True)
        collected_text.append(text[:6000])

        # Pattern: a heading/line with a person's name followed by a role line.
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        for i, line in enumerate(lines[:-1]):
            if len(line) > 40 or not name_re.match(line):
                continue
            nxt = lines[i + 1]
            if len(nxt) <= 60 and any(k in nxt.lower() for k in ROLE_KEYWORDS):
                key = line.lower()
                if key not in seen:
                    seen.add(key)
                    employees.append({"name": line, "role": nxt, "level": _level_for_role(nxt), "source": "scrape"})
        if employees:
            break

    return employees, "\n\n".join(collected_text)[:8000]
