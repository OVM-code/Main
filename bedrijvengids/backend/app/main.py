import hashlib
import hmac
import logging
import os
from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import schemas
from .db import Base, engine, get_db
from .models import Company, Employee, Search, Template, UsageEvent
from .services import exports, personalize, prompts
from .services.osm import OsmError, search_companies
from .services.scraper import enrich_from_website, find_employees

logging.basicConfig(level=logging.INFO)

APP_PASSWORD = os.environ.get("BG_PASSWORD", "demo")
SECRET = os.environ.get("BG_SECRET", "bedrijvengids-dev-secret")
MONTHLY_CREDIT_LIMIT = int(os.environ.get("BG_CREDIT_LIMIT", "40000"))

CREDITS_PER_COMPANY = 5
CREDITS_PER_ENRICH = 2
CREDITS_PER_EMPLOYEE_SEARCH = 2

app = FastAPI(title="Bedrijvengids.AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_EMAIL_TEMPLATE = {
    "kind": "email",
    "subject": "Samenwerking met {bedrijfsnaam}",
    "body": (
        "Beste {zaakvoerder},\n\n"
        "Ik neem contact met u op namens [Uw Bedrijfsnaam].\n\n"
        "Wij helpen bedrijven zoals {bedrijfsnaam} met [uw dienst/product].\n\n"
        "Zou u openstaan voor een kort gesprek om te bespreken hoe wij ook u kunnen helpen?\n\n"
        "Met vriendelijke groet,\n[Uw Naam]"
    ),
    "personalization": "basic",
}

DEFAULT_LINKEDIN_TEMPLATE = {
    "kind": "linkedin",
    "subject": None,
    "body": (
        "Dag {zaakvoerder}, ik kwam {bedrijfsnaam} tegen en was onder de indruk van jullie werk in {gemeente}. "
        "Graag zou ik even connecteren — wij helpen bedrijven zoals dat van jou met [uw dienst/product]."
    ),
    "personalization": "basic",
}


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as db:  # type: Session
        for default in (DEFAULT_EMAIL_TEMPLATE, DEFAULT_LINKEDIN_TEMPLATE):
            if not db.scalar(select(Template).where(Template.kind == default["kind"])):
                db.add(Template(**default))
        db.commit()


# ---------------------------------------------------------------- auth

def _token() -> str:
    return hmac.new(SECRET.encode(), APP_PASSWORD.encode(), hashlib.sha256).hexdigest()


def require_auth(authorization: str = Header(default="")) -> None:
    if authorization != f"Bearer {_token()}":
        raise HTTPException(status_code=401, detail="Niet ingelogd")


@app.post("/api/auth/login", response_model=schemas.LoginResponse)
def login(req: schemas.LoginRequest):
    if req.password != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Ongeldig wachtwoord")
    return {"token": _token()}


# ---------------------------------------------------------------- helpers

def _month_usage(db: Session) -> int:
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    return db.scalar(
        select(func.coalesce(func.sum(UsageEvent.credits), 0)).where(UsageEvent.created_at >= month_start)
    )


def _charge(db: Session, kind: str, credits: int) -> None:
    if credits <= 0:
        return
    if _month_usage(db) + credits > MONTHLY_CREDIT_LIMIT:
        raise HTTPException(status_code=402, detail="Maandelijkse creditlimiet bereikt")
    db.add(UsageEvent(kind=kind, credits=credits))


def _get_company(db: Session, company_id: int) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Bedrijf niet gevonden")
    return company


def _search_out(s: Search, count: int) -> dict:
    return {
        "id": s.id,
        "sector": s.sector,
        "location": s.location,
        "country": s.country,
        "kind": s.kind,
        "functie": s.functie,
        "credits_used": s.credits_used,
        "created_at": s.created_at,
        "company_count": count,
    }


# ---------------------------------------------------------------- stats

@app.get("/api/stats", response_model=schemas.StatsOut, dependencies=[Depends(require_auth)])
def stats(db: Session = Depends(get_db)):
    return {
        "search_count": db.scalar(select(func.count(Search.id))) or 0,
        "company_count": db.scalar(select(func.count(Company.id))) or 0,
        "monthly_credits_used": _month_usage(db),
        "monthly_credit_limit": MONTHLY_CREDIT_LIMIT,
    }


# ---------------------------------------------------------------- searches

@app.post("/api/searches", response_model=schemas.SearchDetail, dependencies=[Depends(require_auth)])
def create_search(req: schemas.SearchCreate, db: Session = Depends(get_db)):
    try:
        found = search_companies(req.sector, req.location, req.country)
    except OsmError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not found:
        raise HTTPException(
            status_code=404,
            detail=f"Geen bedrijven gevonden voor '{req.sector}' in {req.location}. Probeer een andere sector of ruimere locatie.",
        )

    credits = len(found) * CREDITS_PER_COMPANY
    _charge(db, "search", credits)

    search = Search(
        sector=req.sector.strip(),
        location=req.location.strip(),
        country=(req.country or "België").strip(),
        kind=req.kind,
        functie=(req.functie or "").strip() or None,
        credits_used=credits,
    )
    db.add(search)
    db.flush()
    for item in found:
        db.add(Company(search_id=search.id, **item))
    db.commit()
    db.refresh(search)
    out = _search_out(search, len(search.companies))
    out["companies"] = search.companies
    return out


@app.get("/api/searches", response_model=list[schemas.SearchOut], dependencies=[Depends(require_auth)])
def list_searches(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Search, func.count(Company.id))
        .outerjoin(Company)
        .group_by(Search.id)
        .order_by(Search.created_at.desc())
    ).all()
    return [_search_out(s, count) for s, count in rows]


@app.get("/api/searches/{search_id}", response_model=schemas.SearchDetail, dependencies=[Depends(require_auth)])
def get_search(search_id: int, db: Session = Depends(get_db)):
    search = db.get(Search, search_id)
    if not search:
        raise HTTPException(status_code=404, detail="Zoekopdracht niet gevonden")
    out = _search_out(search, len(search.companies))
    out["companies"] = search.companies
    return out


@app.delete("/api/searches/{search_id}", dependencies=[Depends(require_auth)])
def delete_search(search_id: int, db: Session = Depends(get_db)):
    search = db.get(Search, search_id)
    if not search:
        raise HTTPException(status_code=404, detail="Zoekopdracht niet gevonden")
    db.delete(search)
    db.commit()
    return {"ok": True}


# ---------------------------------------------------------------- companies

@app.patch("/api/companies/{company_id}", response_model=schemas.CompanyOut, dependencies=[Depends(require_auth)])
def patch_company(company_id: int, patch: schemas.CompanyPatch, db: Session = Depends(get_db)):
    company = _get_company(db, company_id)
    data = patch.model_dump(exclude_unset=True)
    if data.get("contacted") is True and not company.contacted:
        company.contacted_at = datetime.utcnow()
    for key, value in data.items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


@app.post("/api/companies/{company_id}/enrich", response_model=schemas.CompanyOut, dependencies=[Depends(require_auth)])
def enrich_company(company_id: int, db: Session = Depends(get_db)):
    company = _get_company(db, company_id)
    if not company.website:
        raise HTTPException(status_code=400, detail="Geen website om te analyseren")
    _charge(db, "enrich", CREDITS_PER_ENRICH)

    result = enrich_from_website(company.website)
    for field in ("email", "phone", "vat", "zaakvoerder", "description", "facebook", "instagram", "linkedin"):
        if result.get(field) and not getattr(company, field):
            setattr(company, field, result[field])
    if result.get("pages_text"):
        company.pages_text = result["pages_text"]
    company.enriched = True
    db.commit()
    db.refresh(company)
    return company


@app.get("/api/companies/{company_id}/employees", response_model=list[schemas.EmployeeOut], dependencies=[Depends(require_auth)])
def list_employees(company_id: int, db: Session = Depends(get_db)):
    _get_company(db, company_id)
    return db.scalars(select(Employee).where(Employee.company_id == company_id)).all()


@app.post("/api/companies/{company_id}/employees/find", response_model=list[schemas.EmployeeOut], dependencies=[Depends(require_auth)])
def find_company_employees(company_id: int, db: Session = Depends(get_db)):
    company = _get_company(db, company_id)
    if not company.website:
        raise HTTPException(status_code=400, detail="Geen website om te doorzoeken")
    _charge(db, "employees", CREDITS_PER_EMPLOYEE_SEARCH)

    employees, team_text = find_employees(company.website)
    if team_text:
        company.team_text = team_text

    existing = {e.name.lower() for e in company.employees}
    for emp in employees:
        if emp["name"].lower() not in existing:
            db.add(Employee(company_id=company.id, **emp))
    db.commit()
    return db.scalars(select(Employee).where(Employee.company_id == company_id)).all()


@app.get("/api/companies/{company_id}/message", response_model=schemas.MessageOut, dependencies=[Depends(require_auth)])
def company_message(company_id: int, kind: str = Query("email", pattern="^(email|linkedin)$"), db: Session = Depends(get_db)):
    company = _get_company(db, company_id)
    template = db.scalar(select(Template).where(Template.kind == kind))
    return personalize.build_message(company, template, kind)


# ---------------------------------------------------------------- people search

@app.get("/api/people", response_model=list[schemas.PersonOut], dependencies=[Depends(require_auth)])
def people(
    functie: str | None = None,
    locatie: str | None = None,
    sector: str | None = None,
    level: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Employee, Company).join(Company, Employee.company_id == Company.id)
    rows = db.execute(stmt).all()
    out = []
    for emp, comp in rows:
        if functie and functie.lower() not in (emp.role or "").lower() and functie.lower() not in (emp.level or "").lower():
            continue
        if locatie and locatie.lower() not in (comp.gemeente or "").lower() and locatie.lower() not in (comp.address or "").lower():
            continue
        if sector and sector.lower() not in (comp.category or "").lower():
            continue
        if level and level != (emp.level or ""):
            continue
        out.append(
            {
                "id": emp.id,
                "name": emp.name,
                "role": emp.role,
                "level": emp.level,
                "email": emp.email,
                "phone": emp.phone,
                "linkedin": emp.linkedin,
                "company_id": comp.id,
                "company_name": comp.name,
                "gemeente": comp.gemeente,
                "sector": comp.category,
                "website": comp.website,
            }
        )
    return out


# ---------------------------------------------------------------- templates

@app.get("/api/templates/{kind}", response_model=schemas.TemplateOut, dependencies=[Depends(require_auth)])
def get_template(kind: str, db: Session = Depends(get_db)):
    template = db.scalar(select(Template).where(Template.kind == kind))
    if not template:
        raise HTTPException(status_code=404, detail="Template niet gevonden")
    return template


@app.put("/api/templates/{kind}", response_model=schemas.TemplateOut, dependencies=[Depends(require_auth)])
def put_template(kind: str, req: schemas.TemplateUpdate, db: Session = Depends(get_db)):
    if kind not in ("email", "linkedin"):
        raise HTTPException(status_code=400, detail="Onbekende template")
    template = db.scalar(select(Template).where(Template.kind == kind))
    if not template:
        template = Template(kind=kind)
        db.add(template)
    template.subject = req.subject
    template.body = req.body
    template.personalization = req.personalization
    db.commit()
    db.refresh(template)
    return template


# ---------------------------------------------------------------- Claude prompt flow

@app.post("/api/ai/prompt", response_model=schemas.AiPromptResponse, dependencies=[Depends(require_auth)])
def ai_prompt(req: schemas.AiPromptRequest, db: Session = Depends(get_db)):
    companies = db.scalars(select(Company).where(Company.id.in_(req.company_ids))).all()
    if not companies:
        raise HTTPException(status_code=400, detail="Geen bedrijven geselecteerd")

    if req.type == "enrich":
        pages = {c.id: c.pages_text for c in companies if c.pages_text}
        prompt = prompts.enrich_prompt(companies, pages)
    elif req.type == "employees":
        pages = {c.id: c.team_text for c in companies if c.team_text}
        prompt = prompts.employees_prompt(companies, pages)
    else:
        template = db.scalar(select(Template).where(Template.kind == ("email" if req.type == "email" else "linkedin")))
        if not template:
            raise HTTPException(status_code=400, detail="Stel eerst een template in")
        prompt = prompts.email_prompt(companies, template) if req.type == "email" else prompts.linkedin_prompt(companies, template)

    return {"prompt": prompt, "company_count": len(companies)}


@app.post("/api/ai/apply", response_model=schemas.AiApplyResponse, dependencies=[Depends(require_auth)])
def ai_apply(req: schemas.AiApplyRequest, db: Session = Depends(get_db)):
    try:
        items = prompts.extract_json(req.payload)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Kon JSON niet lezen: {exc}") from exc
    if not isinstance(items, list):
        raise HTTPException(status_code=400, detail="Verwachtte een JSON-array")

    ids = [item.get("id") for item in items if isinstance(item, dict) and item.get("id")]
    companies_by_id = {
        c.id: c for c in db.scalars(select(Company).where(Company.id.in_(ids))).all()
    }

    if req.type == "enrich":
        applied = prompts.apply_enrich(items, companies_by_id)
    elif req.type == "email":
        applied = prompts.apply_email(items, companies_by_id)
    elif req.type == "linkedin":
        applied = prompts.apply_linkedin(items, companies_by_id)
    else:
        applied, new_employees = prompts.apply_employees(items, companies_by_id)
        for emp in new_employees:
            existing = db.scalar(
                select(Employee).where(
                    Employee.company_id == emp["company_id"], func.lower(Employee.name) == emp["name"].lower()
                )
            )
            if not existing:
                db.add(Employee(**emp))

    db.commit()
    return {"applied": applied, "skipped": len(items) - applied, "errors": []}


# ---------------------------------------------------------------- export

@app.get("/api/searches/{search_id}/export", dependencies=[Depends(require_auth)])
def export_search(search_id: int, format: str = Query("csv", pattern="^(csv|xlsx|hubspot)$"), db: Session = Depends(get_db)):
    search = db.get(Search, search_id)
    if not search:
        raise HTTPException(status_code=404, detail="Zoekopdracht niet gevonden")
    companies = search.companies
    slug = f"{search.sector}-{search.location}".replace(" ", "_").lower()

    if format == "xlsx":
        return Response(
            exports.to_xlsx(companies),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{slug}.xlsx"'},
        )
    hubspot = format == "hubspot"
    return Response(
        exports.to_csv(companies, hubspot=hubspot),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{slug}{"-hubspot" if hubspot else ""}.csv"'},
    )
