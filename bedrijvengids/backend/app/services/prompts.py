"""Claude-subscription AI flow: generate copy-paste prompts and apply results.

Instead of calling an LLM API, the app produces a self-contained prompt the
user pastes into claude.ai (or Claude Code). Claude answers with a JSON block
that is pasted back and applied to the database. Same results, no API costs.
"""

import json
import re

from ..models import Company, Template
from .scraper import _level_for_role


def _company_context(c: Company, include_pages: dict[int, str] | None = None) -> dict:
    ctx = {
        "id": c.id,
        "bedrijfsnaam": c.name,
        "gemeente": c.gemeente,
        "categorie": c.category,
        "website": c.website,
        "omschrijving": c.description,
        "zaakvoerder": c.zaakvoerder,
    }
    if include_pages and c.id in include_pages:
        ctx["website_tekst"] = include_pages[c.id]
    return {k: v for k, v in ctx.items() if v}


def enrich_prompt(companies: list[Company], pages: dict[int, str]) -> str:
    data = [_company_context(c, pages) for c in companies]
    return f"""Je bent een B2B-data-analist. Hieronder staat een JSON-lijst van Belgische bedrijven, sommige met ruwe tekst van hun website ("website_tekst").

Voor elk bedrijf, lever aan (voor zover afleidbaar uit de gegevens of publiek bekende informatie):
- "omschrijving": een korte professionele bedrijfsomschrijving in het Nederlands (2-3 zinnen)
- "zaakvoerder": de naam van de zaakvoerder/eigenaar (alleen indien vermeld)
- "btw": het BTW-nummer in formaat BE0xxx.xxx.xxx (alleen indien vermeld)

INPUT:
```json
{json.dumps(data, ensure_ascii=False, indent=2)}
```

Antwoord met UITSLUITEND een JSON-array in een codeblok, één object per bedrijf:
```json
[{{"id": 1, "omschrijving": "...", "zaakvoerder": "...", "btw": "..."}}]
```
Laat velden weg die je niet kan afleiden. Verzin niets."""


def email_prompt(companies: list[Company], template: Template) -> str:
    data = [_company_context(c) for c in companies]
    return f"""Je bent een B2B-sales-copywriter. Hieronder staat een e-mailtemplate en een JSON-lijst van prospects.

Pas per prospect ongeveer 20% van de e-mail aan op basis van de bedrijfsomschrijving, sector en gemeente: persoonlijke aanspreking (gebruik de zaakvoerder-naam indien beschikbaar) en 1-2 zinnen context waarom het aanbod relevant is voor dít bedrijf. Behoud de kernboodschap, toon en lengte van de template. Schrijf in het Nederlands.

TEMPLATE ONDERWERP: {template.subject or ""}
TEMPLATE INHOUD:
\"\"\"
{template.body}
\"\"\"

PROSPECTS:
```json
{json.dumps(data, ensure_ascii=False, indent=2)}
```

Antwoord met UITSLUITEND een JSON-array in een codeblok:
```json
[{{"id": 1, "subject": "...", "body": "..."}}]
```"""


def linkedin_prompt(companies: list[Company], template: Template) -> str:
    data = [_company_context(c) for c in companies]
    return f"""Je bent een B2B-sales-copywriter. Hieronder staat een LinkedIn-berichttemplate en een JSON-lijst van prospects.

Personaliseer het bericht per prospect (max 300 tekens, geschikt als LinkedIn-connectiebericht): persoonlijke aanspreking en korte relevante context. Schrijf in het Nederlands.

TEMPLATE:
\"\"\"
{template.body}
\"\"\"

PROSPECTS:
```json
{json.dumps(data, ensure_ascii=False, indent=2)}
```

Antwoord met UITSLUITEND een JSON-array in een codeblok:
```json
[{{"id": 1, "message": "..."}}]
```"""


def employees_prompt(companies: list[Company], pages: dict[int, str]) -> str:
    data = [_company_context(c, pages) for c in companies]
    return f"""Je bent een recruitment-researcher. Hieronder staat een JSON-lijst van bedrijven met ruwe tekst van hun team-/overons-pagina's ("website_tekst").

Haal per bedrijf alle vermelde medewerkers eruit met hun functie. Neem alleen echte personen op die in de tekst staan — verzin niemand.

INPUT:
```json
{json.dumps(data, ensure_ascii=False, indent=2)}
```

Antwoord met UITSLUITEND een JSON-array in een codeblok:
```json
[{{"id": 1, "medewerkers": [{{"naam": "Jan Jansen", "functie": "Office Manager", "email": null, "linkedin": null}}]}}]
```"""


def extract_json(payload: str):
    """Parse the JSON Claude returned, tolerating markdown fences and prose."""
    text = payload.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    else:
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end > start:
            text = text[start : end + 1]
    return json.loads(text)


def apply_enrich(items: list[dict], companies_by_id: dict[int, Company]) -> int:
    applied = 0
    for item in items:
        c = companies_by_id.get(item.get("id"))
        if not c:
            continue
        if item.get("omschrijving"):
            c.description = str(item["omschrijving"])[:600]
        if item.get("zaakvoerder"):
            c.zaakvoerder = str(item["zaakvoerder"])[:200]
        if item.get("btw"):
            c.vat = str(item["btw"])[:50]
        c.enriched = True
        applied += 1
    return applied


def apply_email(items: list[dict], companies_by_id: dict[int, Company]) -> int:
    applied = 0
    for item in items:
        c = companies_by_id.get(item.get("id"))
        if not c or not item.get("body"):
            continue
        c.ai_email_subject = item.get("subject")
        c.ai_email_body = item["body"]
        applied += 1
    return applied


def apply_linkedin(items: list[dict], companies_by_id: dict[int, Company]) -> int:
    applied = 0
    for item in items:
        c = companies_by_id.get(item.get("id"))
        if not c or not item.get("message"):
            continue
        c.ai_linkedin_message = item["message"]
        applied += 1
    return applied


def apply_employees(items: list[dict], companies_by_id: dict[int, Company]) -> tuple[int, list[dict]]:
    """Returns (companies touched, list of new employee dicts with company_id)."""
    new_employees: list[dict] = []
    touched = 0
    for item in items:
        c = companies_by_id.get(item.get("id"))
        if not c:
            continue
        members = item.get("medewerkers") or []
        for m in members:
            if not m.get("naam"):
                continue
            role = m.get("functie") or ""
            new_employees.append(
                {
                    "company_id": c.id,
                    "name": str(m["naam"])[:200],
                    "role": role[:200] or None,
                    "level": _level_for_role(role) if role else None,
                    "email": m.get("email"),
                    "linkedin": m.get("linkedin"),
                    "source": "claude",
                }
            )
        touched += 1
    return touched, new_employees
