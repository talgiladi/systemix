from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from systemix_mcp_server.config import LoggingSettings


class JsonLogFormatter(logging.Formatter):
    """Small structured formatter for production-friendly console logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id

        extras = getattr(record, "extra_fields", None)
        if isinstance(extras, dict):
            payload.update(extras)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(settings: LoggingSettings) -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    resolved_level = getattr(logging, settings.level.upper(), logging.INFO)

    handler = logging.StreamHandler()
    if settings.format.lower() == "json":
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S%z",
            )
        )

    root_logger.addHandler(handler)
    root_logger.setLevel(resolved_level)

    # Route framework and server logs through the same handler so DEBUG-level
    # MCP activity shows up consistently next to application logs.
    for logger_name in (
        "systemix_mcp_server",
        "mcp",
        "mcp.server",
        "mcp.server.fastmcp",
        "mcp.server.lowlevel.server",
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
    ):
        named_logger = logging.getLogger(logger_name)
        named_logger.handlers.clear()
        named_logger.setLevel(resolved_level)
        named_logger.propagate = True
