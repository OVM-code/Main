"""Unit tests for the rule-based extraction and OSM parsing helpers."""

from app.services.osm import _build_address, _overpass_query
from app.services.prompts import extract_json
from app.services.scraper import _extract_owner, _extract_vat, _level_for_role, _pick_email
from app.services.sectors import resolve_sector


def test_resolve_sector_known():
    tags, label, matched = resolve_sector("vastgoedmakelaar")
    assert matched
    assert ("office", "estate_agent") in tags
    assert label == "Vastgoedmakelaar"


def test_resolve_sector_unknown_falls_back():
    tags, label, matched = resolve_sector("hoefsmid")
    assert not matched
    assert tags == []
    assert label == "Hoefsmid"


def test_overpass_query_with_area_and_tags():
    q = _overpass_query({"area_id": 3600012345}, [("shop", "bakery")], None)
    assert "area(id:3600012345)" in q
    assert 'nwr["shop"="bakery"](area.a);' in q


def test_overpass_query_freetext_fallback():
    q = _overpass_query({"bbox": (50.0, 5.0, 51.0, 6.0)}, [], "hoefsmid")
    assert '["name"~"hoefsmid",i]' in q
    assert "(50.0,5.0,51.0,6.0)" in q


def test_build_address():
    address, city = _build_address(
        {"addr:street": "Helstraat", "addr:housenumber": "18", "addr:postcode": "3721", "addr:city": "Hasselt"}
    )
    assert address == "Helstraat 18, 3721 Hasselt"
    assert city == "Hasselt"


def test_vat_extraction():
    assert _extract_vat("BTW: BE 0416.669.933") == "BE0416.669.933"
    assert _extract_vat("Ondernemingsnummer 0416 669 933") == "BE0416.669.933"
    assert _extract_vat("btw be0416669933") == "BE0416.669.933"
    assert _extract_vat("geen nummer hier") is None


def test_owner_extraction():
    assert _extract_owner("Jan Peeters, zaakvoerder van het bedrijf") == "Jan Peeters"
    assert _extract_owner("Zaakvoerder: Veronique Houben") == "Veronique Houben"
    assert _extract_owner("Onze CEO Miguel Degeneffe leidt het team") == "Miguel Degeneffe"
    assert _extract_owner("gewone tekst zonder namen") is None


def test_pick_email_prefers_own_domain_info():
    emails = ["noreply@mailchimp.com", "jan@houbennv.be", "info@houbennv.be"]
    assert _pick_email(emails, "https://www.houbennv.be") == "info@houbennv.be"


def test_level_for_role():
    assert _level_for_role("CEO & oprichter") == "C-Level"
    assert _level_for_role("Managing Partner") == "Directeur"
    assert _level_for_role("Office Manager") == "Manager"
    assert _level_for_role("Metser") == "Medewerker"


def test_extract_json_variants():
    assert extract_json('```json\n[{"id": 1}]\n```') == [{"id": 1}]
    assert extract_json('[{"id": 2}]') == [{"id": 2}]
    assert extract_json('Hier is het resultaat:\n[{"id": 3}] hopelijk helpt dit') == [{"id": 3}]
