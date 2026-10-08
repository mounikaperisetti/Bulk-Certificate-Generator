from datetime import date

from pydantic import BaseModel, EmailStr, Field


class RecipientInput(BaseModel):
    """Validates one certificate recipient."""

    name: str = Field(min_length=1)
    email: EmailStr


class CertificateData(BaseModel):
    """Validates optional information used on the certificate."""

    organization: str | None = Field(default=None, min_length=1)
    course_name: str | None = Field(default=None, min_length=1)
    start_date: date | None = None
    end_date: date | None = None
    completion_date: date | None = None
    event_name: str | None = Field(default=None, min_length=1)
    event_date: date | None = None


class CertificateGenerationRequestInput(BaseModel):
    """Validates a bulk certificate generation request."""

    certificate_data: CertificateData = Field(
        default_factory=CertificateData
    )
    recipients: list[RecipientInput] = Field(min_length=1)
    