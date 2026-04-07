from __future__ import annotations

import json
import logging
from time import perf_counter
from typing import Any
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


def _summarize_for_log(value: Any, *, max_string_length: int = 200) -> Any:
    if isinstance(value, dict):
        return {str(key): _summarize_for_log(item, max_string_length=max_string_length) for key, item in value.items()}
    if isinstance(value, list):
        return [_summarize_for_log(item, max_string_length=max_string_length) for item in value]
    if isinstance(value, tuple):
        return [_summarize_for_log(item, max_string_length=max_string_length) for item in value]
    if isinstance(value, str) and len(value) > max_string_length:
        return f"{value[:max_string_length]}... [truncated]"
    return value


def _extract_mcp_log_entry(body_text: str | None) -> tuple[str, dict[str, Any]] | None:
    if not body_text:
        return None

    try:
        payload = json.loads(body_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    method = payload.get("method")
    if not isinstance(method, str):
        return None

    fields: dict[str, Any] = {
        "rpc_method": method,
        "rpc_id": payload.get("id"),
    }
    params = payload.get("params")
    if isinstance(params, dict):
        if method == "tools/call":
            fields["tool_name"] = params.get("name")
            fields["tool_arguments"] = _summarize_for_log(params.get("arguments"))
            return "MCP tool call", fields
        if method == "prompts/get":
            fields["prompt_name"] = params.get("name")
            fields["prompt_arguments"] = _summarize_for_log(params.get("arguments"))
            return "MCP prompt call", fields
        if method == "resources/read":
            fields["resource_uri"] = params.get("uri")
            return "MCP resource read", fields

    return "MCP request", fields


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, log_request_bodies: bool = False) -> None:
        super().__init__(app)
        self.log_request_bodies = log_request_bodies

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid4()))
        request.state.request_id = request_id

        body_text: str | None = None
        mcp_request_log: tuple[str, dict[str, Any]] | None = None
        should_capture_body = request.method in {"POST", "PUT", "PATCH"} and (
            self.log_request_bodies or request.url.path.startswith("/mcp")
        )
        if should_capture_body:
            body = await request.body()
            decoded_body = body.decode("utf-8", errors="replace")
            if self.log_request_bodies:
                body_text = decoded_body
            if request.url.path.startswith("/mcp"):
                mcp_request_log = _extract_mcp_log_entry(decoded_body)
            body_was_sent = False

            async def receive() -> dict[str, object]:
                nonlocal body_was_sent
                if body_was_sent:
                    return {"type": "http.request", "body": b"", "more_body": False}

                body_was_sent = True
                return {"type": "http.request", "body": body, "more_body": False}

            request._receive = receive

        started = perf_counter()
        logger.info(
            "Incoming request",
            extra={
                "request_id": request_id,
                "extra_fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else None,
                    "query": str(request.url.query) or None,
                    "body": body_text,
                },
            },
        )
        if mcp_request_log is not None:
            message, extra_fields = mcp_request_log
            logger.debug(
                message,
                extra={
                    "request_id": request_id,
                    "extra_fields": {
                        "path": request.url.path,
                        **extra_fields,
                    },
                },
            )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((perf_counter() - started) * 1000, 3)
            logger.exception(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "extra_fields": {
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": duration_ms,
                    },
                },
            )
            raise

        duration_ms = round((perf_counter() - started) * 1000, 3)
        response.headers["x-request-id"] = request_id
        logger.info(
            "Outgoing response",
            extra={
                "request_id": request_id,
                "extra_fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            },
        )
        return response
