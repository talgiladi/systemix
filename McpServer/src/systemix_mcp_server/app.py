from __future__ import annotations

import contextlib
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from systemix_mcp_server.config import Settings, load_settings
from systemix_mcp_server.logging_config import configure_logging
from systemix_mcp_server.mcp_server import build_mcp_server
from systemix_mcp_server.middleware import RequestContextMiddleware
from systemix_mcp_server.services import SystemixMcpService


logger = logging.getLogger(__name__)

BROWSER_PAGE = Path(__file__).resolve().parent / "browser" / "index.html"


async def docs_redirect() -> RedirectResponse:
    return RedirectResponse("/browser")


async def healthcheck(request: Request) -> dict[str, str]:
    return {
        "status": "ok",
        "request_id": request.state.request_id,
    }


async def browser_test_page() -> HTMLResponse:
    return HTMLResponse(BROWSER_PAGE.read_text(encoding="utf-8"))


def create_app(
    settings: Settings | None = None,
    include_mcp_server: bool = True,
) -> FastAPI:
    resolved_settings = settings or load_settings()
    configure_logging(resolved_settings.logging)

    service = SystemixMcpService(resolved_settings)
    mcp_server = (
        build_mcp_server(resolved_settings, service)
        if include_mcp_server
        else None
    )

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info(
            "Starting Systemix MCP server",
            extra={
                "extra_fields": {
                    "app_name": resolved_settings.app.name,
                    "environment": resolved_settings.app.environment,
                    "known_user_ids": service.known_user_ids(),
                    "issue_types": list(service.issue_types()),
                },
            },
        )
        if mcp_server is None:
            yield
        else:
            async with mcp_server.session_manager.run():
                yield
        logger.info("Systemix MCP server stopped")

    app = FastAPI(
        title=resolved_settings.app.name,
        version=resolved_settings.app.version,
        description="Systemix sample MCP server with browser test harness.",
        lifespan=lifespan,
        swagger_ui_parameters={"tryItOutEnabled": True},
    )
    app.state.settings = resolved_settings
    app.state.service = service
    app.state.mcp_server = mcp_server

    app.add_middleware(
        RequestContextMiddleware,
        log_request_bodies=resolved_settings.logging.log_request_bodies,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.server.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["*"],
        expose_headers=["Mcp-Session-Id", "x-request-id"],
    )

    app.get("/", include_in_schema=False)(docs_redirect)
    app.get("/health")(healthcheck)
    app.get("/browser", response_class=HTMLResponse)(browser_test_page)

    if mcp_server is not None:
        app.mount("/mcp", mcp_server.streamable_http_app())
    return app
