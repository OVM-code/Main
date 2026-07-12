"""Template personalization: placeholder substitution and mailto: building."""

from urllib.parse import quote

from ..models import Company, Template

PLACEHOLDERS = ("bedrijfsnaam", "zaakvoerder", "gemeente")


def render(text: str | None, company: Company) -> str:
    if not text:
        return ""
    values = {
        "bedrijfsnaam": company.name or "",
        # Fall back to the company name so greetings never render as "Beste ,"
        "zaakvoerder": company.zaakvoerder or company.name or "",
        "gemeente": company.gemeente or "",
    }
    out = text
    for key, value in values.items():
        out = out.replace("{" + key + "}", value)
    return out


def build_message(company: Company, template: Template | None, kind: str) -> dict:
    """Return the personalized message for a company.

    AI-personalized versions (pasted back from Claude) take precedence when the
    template's personalization level is 'ai'; otherwise plain placeholder
    substitution is used.
    """
    subject = None
    body = ""
    source = "basic"

    if template:
        subject = render(template.subject, company) if kind == "email" else None
        body = render(template.body, company)
        if template.personalization == "ai":
            if kind == "email" and company.ai_email_body:
                subject = company.ai_email_subject or subject
                body = company.ai_email_body
                source = "ai"
            elif kind == "linkedin" and company.ai_linkedin_message:
                body = company.ai_linkedin_message
                source = "ai"

    mailto = None
    if kind == "email" and company.email:
        mailto = f"mailto:{company.email}?subject={quote(subject or '')}&body={quote(body)}"

    return {
        "subject": subject,
        "body": body,
        "to": company.email if kind == "email" else company.linkedin,
        "mailto": mailto,
        "source": source,
    }
