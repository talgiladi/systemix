"""Contact form endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.schemas.contact import ContactSubmission
from app.services.contact import handle_contact_submission
from app.services.rate_limit import contact_rate_limiter
from app.services.sanitization import sanitize_contact_input


router = APIRouter()


@router.post("/contact", response_class=JSONResponse)
async def submit_contact_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    company: str = Form(""),
    message: str = Form(...),
    website: str = Form(""),
) -> JSONResponse:
    """Validate, sanitize, and forward contact submissions."""

    if website.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid submission.")

    client_id = request.client.host if request.client else "unknown"
    if not contact_rate_limiter.allow(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many submissions. Please try again later.",
        )

    clean_data = sanitize_contact_input(
        name=name,
        email=email,
        company=company,
        message=message,
    )
    submission = ContactSubmission(**clean_data)
    handle_contact_submission(
        submission.name,
        submission.email,
        submission.company,
        submission.message,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Thanks. We’ll review your request and respond shortly."},
    )
