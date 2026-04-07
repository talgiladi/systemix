from __future__ import annotations

import contextlib
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mcp_host.api.routes import router as api_router
from mcp_host.config import Settings, load_settings
from mcp_host.logging_config import configure_logging
from mcp_host.middleware.request_context import RequestContextMiddleware
from mcp_host.services.ask_service import AskService
from mcp_host.services.llm_service import LlmService
from mcp_host.services.remote_mcp_service import RemoteMcpService


logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or load_settings()
    configure_logging(resolved_settings.logging)

    remote_mcp_service = RemoteMcpService(resolved_settings)
    llm_service = LlmService(resolved_settings)
    ask_service = AskService(
        resolved_settings,
        remote_mcp_service=remote_mcp_service,
        llm_service=llm_service,
    )

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info(
            "Starting Systemix MCP host",
            extra={
                "extra_fields": {
                    "app_name": resolved_settings.app.name,
                    "environment": resolved_settings.app.environment,
                    "active_provider": resolved_settings.active_provider,
                    "configured_mcp_servers": [
                        server.name for server in resolved_settings.mcp_servers
                    ],
                },
            },
        )
        try:
            yield
        finally:
            await llm_service.aclose()
            logger.info("Systemix MCP host stopped")

    app = FastAPI(
        title=resolved_settings.app.name,
        version=resolved_settings.app.version,
        description=(
            "HTTP facade for the Systemix MCP host. "
            "Use the interactive docs to submit requests to POST /api/ask."
        ),
        lifespan=lifespan,
        swagger_ui_parameters={"tryItOutEnabled": True},
    )
    app.state.settings = resolved_settings
    app.state.ask_service = ask_service

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.server.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app
