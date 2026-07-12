"""CSV / Excel / HubSpot-import exports for a search's companies."""

import csv
import io

from openpyxl import Workbook

from ..models import Company

COLUMNS = [
    ("Bedrijfsnaam", lambda c: c.name),
    ("Adres", lambda c: c.address),
    ("Gemeente", lambda c: c.gemeente),
    ("Telefoon", lambda c: c.phone),
    ("E-mail", lambda c: c.email),
    ("Website", lambda c: c.website),
    ("Categorie", lambda c: c.category),
    ("Zaakvoerder", lambda c: c.zaakvoerder),
    ("BTW-nummer", lambda c: c.vat),
    ("Omschrijving", lambda c: c.description),
    ("Facebook", lambda c: c.facebook),
    ("Instagram", lambda c: c.instagram),
    ("LinkedIn", lambda c: c.linkedin),
    ("Gecontacteerd", lambda c: "ja" if c.contacted else "nee"),
]

# Column mapping HubSpot's company import recognizes out of the box.
HUBSPOT_COLUMNS = [
    ("Company name", lambda c: c.name),
    ("Company domain name", lambda c: c.website),
    ("Phone number", lambda c: c.phone),
    ("Street address", lambda c: c.address),
    ("City", lambda c: c.gemeente),
    ("Country/Region", lambda c: "Belgium"),
    ("Description", lambda c: c.description),
    ("LinkedIn company page", lambda c: c.linkedin),
]


def to_csv(companies: list[Company], hubspot: bool = False) -> bytes:
    columns = HUBSPOT_COLUMNS if hubspot else COLUMNS
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";" if not hubspot else ",")
    writer.writerow([name for name, _ in columns])
    for c in companies:
        writer.writerow([fn(c) or "" for _, fn in columns])
    # utf-8-sig so Excel opens accented characters correctly
    return buf.getvalue().encode("utf-8-sig")


def to_xlsx(companies: list[Company]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Bedrijven"
    ws.append([name for name, _ in COLUMNS])
    for c in companies:
        ws.append([fn(c) or "" for _, fn in COLUMNS])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
