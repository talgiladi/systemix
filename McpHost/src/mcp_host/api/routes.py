from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from mcp_host.models.api import AskRequest, AskResponse
from mcp_host.services.ask_service import AskService


logger = logging.getLogger(__name__)
router = APIRouter()


def get_ask_service(request: Request) -> AskService:
    return request.app.state.ask_service


@router.get("/", include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@router.get("/health", tags=["system"])
async def healthcheck(request: Request) -> dict[str, str]:
    request_id = getattr(request.state, "request_id", "unknown")
    logger.debug("Healthcheck executed", extra={"request_id": request_id})
    return {"status": "ok", "request_id": request_id}


@router.post(
    "/api/ask",
    response_model=AskResponse,
    tags=["ask"],
    summary="Send a prompt through the MCP host",
    description=(
        "Accepts a user prompt, discovers tools from configured remote MCP servers, "
        "lets the configured LLM decide whether to call them, and returns the final "
        "answer plus tool/telemetry details."
    ),
)
async def ask(
    payload: AskRequest,
    request: Request,
    ask_service: AskService = Depends(get_ask_service),
) -> AskResponse:
    request_id = request.state.request_id
    if request.app.state.settings.logging.log_request_bodies:
        logger.debug(
            "Ask request payload",
            extra={
                "request_id": request_id,
                "extra_fields": {"payload": payload.model_dump(mode="json")},
            },
        )
    return await ask_service.ask(payload, request_id=request_id)
