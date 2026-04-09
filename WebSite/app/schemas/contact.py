"""Contact form schema definitions."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactSubmission(BaseModel):
    """Validated contact submission payload."""

    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    company: str = Field(default="", max_length=120)
    message: str = Field(min_length=20, max_length=2000)

    @field_validator("name", "company", "message")
    @classmethod
    def strip_excess_whitespace(cls, value: str) -> str:
        return " ".join(value.split())
