from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    token: str


class SearchCreate(BaseModel):
    sector: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=200)
    country: str = Field(default="België", max_length=100)
    kind: str = Field(default="companies", pattern="^(companies|people)$")
    functie: str | None = None


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    name: str
    role: str | None
    level: str | None
    email: str | None
    phone: str | None
    linkedin: str | None
    source: str | None


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    search_id: int
    name: str
    address: str | None
    gemeente: str | None
    phone: str | None
    email: str | None
    website: str | None
    category: str | None
    lat: float | None
    lon: float | None
    facebook: str | None
    instagram: str | None
    linkedin: str | None
    description: str | None
    vat: str | None
    zaakvoerder: str | None
    contacted: bool
    contacted_at: datetime | None
    enriched: bool
    ai_email_subject: str | None
    ai_email_body: str | None
    ai_linkedin_message: str | None


class SearchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sector: str
    location: str
    country: str
    kind: str
    functie: str | None
    credits_used: int
    created_at: datetime
    company_count: int = 0


class SearchDetail(SearchOut):
    companies: list[CompanyOut] = []


class CompanyPatch(BaseModel):
    contacted: bool | None = None
    email: str | None = None
    phone: str | None = None
    zaakvoerder: str | None = None
    description: str | None = None


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    kind: str
    subject: str | None
    body: str
    personalization: str


class TemplateUpdate(BaseModel):
    subject: str | None = None
    body: str
    personalization: str = Field(pattern="^(basic|ai)$")


class MessageOut(BaseModel):
    subject: str | None
    body: str
    to: str | None
    mailto: str | None
    source: str  # basic | ai


class StatsOut(BaseModel):
    search_count: int
    company_count: int
    monthly_credits_used: int
    monthly_credit_limit: int


class AiPromptRequest(BaseModel):
    type: str = Field(pattern="^(enrich|email|linkedin|employees)$")
    company_ids: list[int]


class AiPromptResponse(BaseModel):
    prompt: str
    company_count: int


class AiApplyRequest(BaseModel):
    type: str = Field(pattern="^(enrich|email|linkedin|employees)$")
    payload: str  # JSON pasted back from Claude


class AiApplyResponse(BaseModel):
    applied: int
    skipped: int
    errors: list[str] = []


class PersonOut(BaseModel):
    id: int
    name: str
    role: str | None
    level: str | None
    email: str | None
    phone: str | None
    linkedin: str | None
    company_id: int
    company_name: str
    gemeente: str | None
    sector: str | None
    website: str | None
