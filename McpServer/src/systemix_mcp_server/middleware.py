from __future__ import annotations

import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, log_request_bodies: bool = False) -> None:
        super().__init__(app)
        self.log_request_bodies = log_request_bodies

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid4()))
        request.state.request_id = request_id

        body_text: str | None = None
        if self.log_request_bodies and request.method in {"POST", "PUT", "PATCH"}:
            body = await request.body()
            body_text = body.decode("utf-8", errors="replace")

            async def receive() -> dict[str, object]:
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
