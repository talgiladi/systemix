"""Input sanitization helpers."""

from __future__ import annotations

import html


def _clean_text(value: str, *, preserve_newlines: bool = False) -> str:
    raw = value.strip()
    if preserve_newlines:
        collapsed = "\n".join(line.strip() for line in raw.splitlines() if line.strip())
    else:
        collapsed = " ".join(raw.split())
    return html.escape(collapsed, quote=True)


def sanitize_contact_input(name: str, email: str, company: str, message: str) -> dict[str, str]:
    """Sanitize user-submitted contact values before validation and processing."""

    return {
        "name": _clean_text(name),
        "email": email.strip(),
        "company": _clean_text(company),
        "message": _clean_text(message, preserve_newlines=True),
    }
