"""Best-effort geo lookup for first-visit language detection."""

from __future__ import annotations

import asyncio
import ipaddress
import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from fastapi import Request

from app.config import settings
from app.content import DEFAULT_LANGUAGE


logger = logging.getLogger("systemix.geolocation")
ISRAEL_COUNTRY_CODE = "IL"


def extract_client_ip(request: Request) -> str | None:
    """Return the most trustworthy client IP available on the request."""

    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        first_ip = forwarded_for.split(",")[0].strip()
        if first_ip:
            return first_ip

    real_ip = request.headers.get("x-real-ip", "").strip()
    if real_ip:
        return real_ip

    if request.client and request.client.host:
        return request.client.host

    return None


def is_public_ip(value: str | None) -> bool:
    """Return True when the value is a usable public IP address."""

    if not value:
        return False

    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False

    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
        or ip.is_link_local
    )


def _fetch_country_code(client_ip: str) -> str | None:
    """Resolve a country code for an IP address via the configured provider."""

    endpoint = f"{settings.geo_lookup_url.rstrip('/')}/{client_ip}"
    with urlopen(endpoint, timeout=settings.geo_lookup_timeout_seconds) as response:
        payload: dict[str, Any] = json.load(response)

    country_code = payload.get("country")
    if not isinstance(country_code, str):
        return None

    normalized = country_code.strip().upper()
    return normalized or None


async def lookup_country_code(request: Request) -> str | None:
    """Best-effort country detection that never raises to the caller."""

    client_ip = extract_client_ip(request)
    if not is_public_ip(client_ip):
        return None

    try:
        return await asyncio.to_thread(_fetch_country_code, client_ip)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        logger.warning("Geo lookup failed for %s: %s", client_ip, exc)
        return None


def infer_language_from_headers(request: Request) -> str:
    """Use browser language as a soft fallback when geo lookup is unavailable."""

    accept_language = request.headers.get("accept-language", "").lower()
    if accept_language.startswith("he") or ",he" in accept_language:
        return "he"
    return DEFAULT_LANGUAGE


async def detect_language(request: Request) -> str:
    """Resolve the first-visit language with safe fallbacks."""

    country_code = await lookup_country_code(request)
    if country_code == ISRAEL_COUNTRY_CODE:
        return "he"
    if country_code:
        return DEFAULT_LANGUAGE
    return infer_language_from_headers(request)
