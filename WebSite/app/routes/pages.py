"""Template-rendered page routes with localization support."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.content import (
    COMMON_CONTENT,
    DEFAULT_LANGUAGE,
    LANGUAGE_COOKIE_MAX_AGE,
    LANGUAGE_COOKIE_NAME,
    PAGE_CONTENT,
    PAGE_PATHS,
    PAGE_TEMPLATES,
    PATH_TO_PAGE_KEY,
    SUPPORTED_LANGUAGES,
)
from app.services.geolocation import detect_language


BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


def _alternate_language(language: str) -> str:
    return "he" if language == "en" else "en"


def _normalize_language(value: str | None) -> str | None:
    if value in SUPPORTED_LANGUAGES:
        return value
    return None


def _preferred_language_from_cookie(request: Request) -> str | None:
    return _normalize_language(request.cookies.get(LANGUAGE_COOKIE_NAME))


def _set_language_cookie(response: Response, language: str) -> None:
    response.set_cookie(
        key=LANGUAGE_COOKIE_NAME,
        value=language,
        max_age=LANGUAGE_COOKIE_MAX_AGE,
        httponly=False,
        samesite="lax",
    )


def _localized_path(page_key: str, language: str) -> str:
    return PAGE_PATHS[page_key][language]


def _safe_redirect_target(next_path: str | None, language: str) -> str:
    if not next_path:
        return _localized_path("home", language)

    parsed = urlsplit(next_path)
    if parsed.scheme or parsed.netloc:
        return _localized_path("home", language)

    path = parsed.path or _localized_path("home", language)
    if not path.startswith("/"):
        path = f"/{path.lstrip('/')}"

    page_key = PATH_TO_PAGE_KEY.get(path)
    if page_key:
        localized = _localized_path(page_key, language)
    else:
        localized = path

    if language == "he" and not localized.startswith("/he") and localized in PATH_TO_PAGE_KEY:
        page_key = PATH_TO_PAGE_KEY[localized]
        localized = _localized_path(page_key, language)
    elif language == "en" and localized.startswith("/he"):
        page_key = PATH_TO_PAGE_KEY.get(localized)
        if page_key:
            localized = _localized_path(page_key, language)

    if parsed.query:
        return f"{localized}?{parsed.query}"
    return localized


def _build_context(request: Request, page_key: str, language: str) -> dict[str, object]:
    alternate_language = _alternate_language(language)
    page = PAGE_CONTENT[page_key][language]

    return {
        "request": request,
        "page_title": page["page_title"],
        "page_description": page["page_description"],
        "language": language,
        "alternate_language": alternate_language,
        "page_key": page_key,
        "t": COMMON_CONTENT[language],
        "page": page,
        "paths": PAGE_PATHS[page_key],
        "nav_paths": {key: localized[language] for key, localized in PAGE_PATHS.items()},
        "language_switch_urls": {
            lang: f"/language/{lang}?next={PAGE_PATHS[page_key][lang]}"
            for lang in SUPPORTED_LANGUAGES
        },
    }


def _template_response(request: Request, page_key: str, language: str) -> HTMLResponse:
    response = templates.TemplateResponse(
        PAGE_TEMPLATES[page_key],
        _build_context(request, page_key, language),
    )
    _set_language_cookie(response, language)
    return response


async def _english_page(request: Request, page_key: str) -> Response:
    preferred_language = _preferred_language_from_cookie(request)
    if preferred_language == "he":
        return RedirectResponse(_localized_path(page_key, "he"), status_code=307)

    if preferred_language is None:
        detected_language = await detect_language(request)
        if detected_language == "he":
            response = RedirectResponse(_localized_path(page_key, "he"), status_code=307)
            _set_language_cookie(response, "he")
            return response

    return _template_response(request, page_key, "en")


def _localized_page(request: Request, page_key: str, language: str) -> HTMLResponse:
    return _template_response(request, page_key, language)


@router.get("/language/{language}")
async def set_language(language: str, next: str = "/") -> RedirectResponse:
    normalized_language = _normalize_language(language) or DEFAULT_LANGUAGE
    response = RedirectResponse(
        _safe_redirect_target(next, normalized_language),
        status_code=303,
    )
    _set_language_cookie(response, normalized_language)
    return response


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    return await _english_page(request, "home")


@router.get("/use-cases", response_class=HTMLResponse)
async def use_cases(request: Request) -> Response:
    return await _english_page(request, "use_cases")


@router.get("/faq", response_class=HTMLResponse)
async def faq(request: Request) -> Response:
    return await _english_page(request, "faq")


@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request) -> Response:
    return await _english_page(request, "contact")


@router.get("/he", response_class=HTMLResponse)
async def home_he(request: Request) -> HTMLResponse:
    return _localized_page(request, "home", "he")


@router.get("/he/use-cases", response_class=HTMLResponse)
async def use_cases_he(request: Request) -> HTMLResponse:
    return _localized_page(request, "use_cases", "he")


@router.get("/he/faq", response_class=HTMLResponse)
async def faq_he(request: Request) -> HTMLResponse:
    return _localized_page(request, "faq", "he")


@router.get("/he/contact", response_class=HTMLResponse)
async def contact_he(request: Request) -> HTMLResponse:
    return _localized_page(request, "contact", "he")
