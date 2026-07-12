"""Seed the database with demo data (bouwbedrijf in Hasselt, like the pitch deck).

Usage: .venv/bin/python seed_demo.py
Handy for demos without network access; safe to run repeatedly.
"""

from app.db import Base, SessionLocal, engine
from app.models import Company, Employee, Search, UsageEvent

DEMO = [
    dict(name="Ath Bouw", address="Helstraat 18, 3721 Hasselt", gemeente="Hasselt",
         phone="+32 476 74 56 68", email="buildyourhome@embuild.be", website="https://www.embuild.be",
         category="Bouwbedrijf", lat=50.9600, lon=5.3220, instagram="https://instagram.com/athbouw",
         facebook="https://facebook.com/athbouw",
         description="Build Your Home is een initiatief dat particuliere bouwers begeleidt bij hun bouwproject."),
    dict(name="Houben nv", address="Prins-Bisschopssingel 36, 3500 Hasselt", gemeente="Hasselt",
         phone="+32 11 26 96 00", email="info@houbennv.be", website="https://www.houbennv.be",
         category="Bouwbedrijf", lat=50.9210, lon=5.3320, vat="BE0416.669.933",
         facebook="https://facebook.com/houbennv", linkedin="https://linkedin.com/company/houben-nv",
         zaakvoerder="Veronique Houben", enriched=True,
         description="Houben nv is een Klasse 8D-aannemer die sinds 1932 bouwprojecten realiseert voor bouwheren, overheden en architecten."),
    dict(name="Hemabo", address="Herbroekstraat 33, 3720 Hasselt", gemeente="Hasselt",
         phone="+32 475 36 83 82", email="info@hemabo.be", website="https://www.hemabo.be",
         category="Aannemer", lat=50.9420, lon=5.3730, vat="BE0469.768.620",
         description="Hemabo is een bouwbedrijf gespecialiseerd in renovatie en nieuwbouw."),
    dict(name="AN-B Renovatie", address="Mersenhovenstraat 9, 3722 Hasselt", gemeente="Hasselt",
         phone="+32 485 54 69 09", email="amer@an-b.be", website="https://www.an-b.be",
         category="Bouwbedrijf", lat=50.9330, lon=5.4110, vat="BE0701.785.793",
         description="ANB Renovatie is een algemene renovatie-aannemer voor woningen en appartementen."),
    dict(name="NAS-RENOVATIE", address="Bissemstraat 4, 3720 Hasselt", gemeente="Hasselt",
         phone="+32 477 49 62 94", email="info@nasrenovatie.be", website="https://www.nasrenovatie.be",
         category="Bouwbedrijf", lat=50.9480, lon=5.3610, vat="BE0757.993.435",
         description="NAS-RENOVATIE is een gespecialiseerd renovatiebedrijf actief in Limburg."),
    dict(name="GDCprojects", address="Loostraat 18, 3724 Hasselt", gemeente="Hasselt",
         phone="+32 472 29 64 41", email="glenn@gdcprojects.be", website="https://www.gdcprojects.be",
         category="Bouwbedrijf", lat=50.9150, lon=5.4260, vat="BE0753.771.755",
         description="GDC Projects is gespecialiseerd in totaalrenovaties en interieurafwerking."),
]

EMPLOYEES = {
    "Houben nv": [
        ("Jimmy Van De Ven", "Project Manager", "Manager"),
        ("Pieter Vanbuel", "Managing Partner", "Directeur"),
        ("Arne Briers", "Junior Project Manager", "Manager"),
        ("Alex Watte", "Beherend Partner", "Directeur"),
        ("Sam Doncker", "Business Development Manager", "Manager"),
        ("Tina Baldewyns", "Office Manager", "Manager"),
        ("Elias Doncker", "Operations Manager", "Manager"),
    ],
}


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Search).filter_by(sector="bouwbedrijf", location="Hasselt").first()
        if existing:
            print(f"Demo search already exists (id={existing.id}), skipping.")
            return
        credits = len(DEMO) * 5
        search = Search(sector="bouwbedrijf", location="Hasselt", country="België", credits_used=credits)
        db.add(search)
        db.flush()
        for i, item in enumerate(DEMO):
            company = Company(search_id=search.id, osm_ref=f"demo{i}", **item)
            db.add(company)
            db.flush()
            for name, role, level in EMPLOYEES.get(item["name"], []):
                db.add(Employee(company_id=company.id, name=name, role=role, level=level, source="scrape"))
        db.add(UsageEvent(kind="search", credits=credits))
        db.commit()
        print(f"Seeded demo search id={search.id} with {len(DEMO)} companies.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
