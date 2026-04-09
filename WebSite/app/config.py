"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    app_name: str = os.getenv("APP_NAME", "Systemix")
    environment: str = os.getenv("ENVIRONMENT", "development")
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8980"))
    request_log_enabled: bool = os.getenv("REQUEST_LOG_ENABLED", "true").lower() == "true"
    contact_rate_limit: int = int(os.getenv("CONTACT_RATE_LIMIT", "5"))
    contact_rate_window_seconds: int = int(os.getenv("CONTACT_RATE_WINDOW_SECONDS", "600"))


settings = Settings()
