from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Search(Base):
    __tablename__ = "searches"

    id: Mapped[int] = mapped_column(primary_key=True)
    sector: Mapped[str] = mapped_column(String(200))
    location: Mapped[str] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(100), default="België")
    kind: Mapped[str] = mapped_column(String(20), default="companies")  # companies | people
    functie: Mapped[str | None] = mapped_column(String(200), nullable=True)  # for people searches
    credits_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    companies: Mapped[list["Company"]] = relationship(
        back_populates="search", cascade="all, delete-orphan"
    )


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (UniqueConstraint("search_id", "osm_ref", name="uq_company_search_osm"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    search_id: Mapped[int] = mapped_column(ForeignKey("searches.id", ondelete="CASCADE"))
    osm_ref: Mapped[str | None] = mapped_column(String(50), nullable=True)

    name: Mapped[str] = mapped_column(String(300))
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    gemeente: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str | None] = mapped_column(String(200), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    facebook: Mapped[str | None] = mapped_column(String(500), nullable=True)
    instagram: Mapped[str | None] = mapped_column(String(500), nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String(500), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    vat: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zaakvoerder: Mapped[str | None] = mapped_column(String(200), nullable=True)

    contacted: Mapped[bool] = mapped_column(Boolean, default=False)
    contacted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    enriched: Mapped[bool] = mapped_column(Boolean, default=False)

    # Raw scraped text cached for the Claude prompt flow (not exposed in the UI)
    pages_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    team_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    ai_email_subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_email_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_linkedin_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    search: Mapped["Search"] = relationship(back_populates="companies")
    employees: Mapped[list["Employee"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str | None] = mapped_column(String(200), nullable=True)
    level: Mapped[str | None] = mapped_column(String(50), nullable=True)  # C-Level | Directeur | Manager | Medewerker
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # scrape | claude | manual
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="employees")


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(20), unique=True)  # email | linkedin
    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    body: Mapped[str] = mapped_column(Text, default="")
    personalization: Mapped[str] = mapped_column(String(20), default="basic")  # basic | ai


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(50))  # search | enrich | employees
    credits: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
