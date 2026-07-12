"""End-to-end API tests with the OSM layer mocked (no network needed)."""

import os
import tempfile

os.environ["BG_DATA_DIR"] = tempfile.mkdtemp()
os.environ["BG_PASSWORD"] = "demo"

import pytest
from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app

FAKE_COMPANIES = [
    {
        "osm_ref": "n1",
        "name": "Ath Bouw",
        "address": "Helstraat 18, 3721 Hasselt",
        "gemeente": "Hasselt",
        "phone": "+32 476 74 56 68",
        "email": "buildyourhome@embuild.be",
        "website": "https://athbouw.example",
        "category": "Bouwbedrijf",
        "lat": 50.93,
        "lon": 5.34,
        "facebook": None,
        "instagram": None,
        "linkedin": None,
        "description": None,
        "zaakvoerder": None,
    },
    {
        "osm_ref": "w2",
        "name": "Houben nv",
        "address": "Prins-Bisschopssingel 36, 3500 Hasselt",
        "gemeente": "Hasselt",
        "phone": "+32 11 26 96 00",
        "email": None,
        "website": "https://houbennv.example",
        "category": "Bouwbedrijf",
        "lat": 50.92,
        "lon": 5.33,
        "facebook": None,
        "instagram": None,
        "linkedin": None,
        "description": None,
        "zaakvoerder": None,
    },
]


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(main_module, "search_companies", lambda *a, **k: [dict(c) for c in FAKE_COMPANIES])
    with TestClient(app) as tc:
        resp = tc.post("/api/auth/login", json={"password": "demo"})
        assert resp.status_code == 200
        tc.headers["Authorization"] = f"Bearer {resp.json()['token']}"
        yield tc


def test_login_rejects_bad_password():
    with TestClient(app) as tc:
        assert tc.post("/api/auth/login", json={"password": "wrong"}).status_code == 401
        assert tc.get("/api/stats").status_code == 401


def test_full_flow(client):
    # create search
    resp = client.post("/api/searches", json={"sector": "bouwbedrijf", "location": "Hasselt"})
    assert resp.status_code == 200
    search = resp.json()
    assert search["company_count"] == 2
    assert search["credits_used"] == 10
    company_ids = [c["id"] for c in search["companies"]]

    # history + detail
    assert len(client.get("/api/searches").json()) >= 1
    detail = client.get(f"/api/searches/{search['id']}").json()
    assert detail["companies"][0]["name"] == "Ath Bouw"

    # stats and credit accounting
    stats = client.get("/api/stats").json()
    assert stats["monthly_credits_used"] >= 10
    assert stats["monthly_credit_limit"] == 40000

    # mark contacted
    patched = client.patch(f"/api/companies/{company_ids[0]}", json={"contacted": True}).json()
    assert patched["contacted"] is True
    assert patched["contacted_at"] is not None

    # templates: default seeded, then update to AI level
    template = client.get("/api/templates/email").json()
    assert "{bedrijfsnaam}" in template["subject"]
    client.put(
        "/api/templates/email",
        json={"subject": "Samenwerking met {bedrijfsnaam}", "body": "Beste {zaakvoerder},\n{bedrijfsnaam} in {gemeente}.", "personalization": "ai"},
    )

    # message rendering: basic placeholders (no AI version stored yet)
    message = client.get(f"/api/companies/{company_ids[0]}/message?kind=email").json()
    assert "Ath Bouw" in message["subject"]
    assert message["source"] == "basic"
    assert message["mailto"].startswith("mailto:buildyourhome@embuild.be")

    # Claude prompt flow: email personalization
    prompt = client.post("/api/ai/prompt", json={"type": "email", "company_ids": company_ids}).json()
    assert "Ath Bouw" in prompt["prompt"]
    payload = f'```json\n[{{"id": {company_ids[0]}, "subject": "Hallo Ath Bouw", "body": "Persoonlijke mail"}}]\n```'
    applied = client.post("/api/ai/apply", json={"type": "email", "payload": payload}).json()
    assert applied["applied"] == 1

    message = client.get(f"/api/companies/{company_ids[0]}/message?kind=email").json()
    assert message["source"] == "ai"
    assert message["body"] == "Persoonlijke mail"

    # Claude prompt flow: enrichment
    payload = f'[{{"id": {company_ids[1]}, "omschrijving": "Klasse 8-aannemer.", "zaakvoerder": "Veronique Houben", "btw": "BE0416.669.933"}}]'
    applied = client.post("/api/ai/apply", json={"type": "enrich", "payload": payload}).json()
    assert applied["applied"] == 1
    detail = client.get(f"/api/searches/{search['id']}").json()
    houben = next(c for c in detail["companies"] if c["name"] == "Houben nv")
    assert houben["vat"] == "BE0416.669.933"
    assert houben["zaakvoerder"] == "Veronique Houben"

    # Claude prompt flow: employees
    payload = f'[{{"id": {houben["id"]}, "medewerkers": [{{"naam": "Jimmy Van De Ven", "functie": "Project Manager"}}, {{"naam": "Pieter Vanbuel", "functie": "Managing Partner"}}]}}]'
    applied = client.post("/api/ai/apply", json={"type": "employees", "payload": payload}).json()
    assert applied["applied"] == 1
    employees = client.get(f"/api/companies/{houben['id']}/employees").json()
    assert {e["name"] for e in employees} == {"Jimmy Van De Ven", "Pieter Vanbuel"}
    assert next(e for e in employees if e["name"] == "Pieter Vanbuel")["level"] == "Directeur"

    # people search across companies
    people = client.get("/api/people?functie=project").json()
    assert any(p["name"] == "Jimmy Van De Ven" for p in people)
    assert people[0]["company_name"] == "Houben nv"
    assert client.get("/api/people?level=C-Level").json() == []

    # exports
    csv_resp = client.get(f"/api/searches/{search['id']}/export?format=csv")
    assert csv_resp.status_code == 200
    assert "Ath Bouw" in csv_resp.text
    xlsx_resp = client.get(f"/api/searches/{search['id']}/export?format=xlsx")
    assert xlsx_resp.status_code == 200
    assert len(xlsx_resp.content) > 1000
    hub_resp = client.get(f"/api/searches/{search['id']}/export?format=hubspot")
    assert "Company name" in hub_resp.text

    # delete cascades
    assert client.delete(f"/api/searches/{search['id']}").status_code == 200
    assert client.get(f"/api/searches/{search['id']}").status_code == 404


def test_search_not_found_message(client, monkeypatch):
    monkeypatch.setattr(main_module, "search_companies", lambda *a, **k: [])
    resp = client.post("/api/searches", json={"sector": "onbestaand", "location": "Nergens"})
    assert resp.status_code == 404
