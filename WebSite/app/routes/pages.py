"""Template-rendered page routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


def _build_context(request: Request, page_title: str, page_description: str) -> dict[str, object]:
    return {
        "request": request,
        "page_title": page_title,
        "page_description": page_description,
    }


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    context = _build_context(
        request,
        "Systemix | AI-Powered Business Automation",
        "Systemix designs secure, reliable AI automation systems for modern business operations.",
    )
    return templates.TemplateResponse("home.html", context)


@router.get("/use-cases", response_class=HTMLResponse)
async def use_cases(request: Request) -> HTMLResponse:
    context = _build_context(
        request,
        "Use Cases | Systemix",
        "Explore practical AI automation use cases, from CRM orchestration to internal knowledge systems.",
    )
    return templates.TemplateResponse("use_cases.html", context)


@router.get("/faq", response_class=HTMLResponse)
async def faq(request: Request) -> HTMLResponse:
    context = _build_context(
        request,
        "FAQ | Systemix",
        "Answers to practical questions about deployment, security, integrations, and AI system reliability.",
    )
    return templates.TemplateResponse("faq.html", context)
