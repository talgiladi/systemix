from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from systemix_mcp_server.models import AccountRecord, SupportSettingsModel


DEFAULT_CONFIG_PATH = Path("config.json")
CONFIG_PATH_ENV_VAR = "SYSTEMIX_MCP_SERVER_CONFIG_PATH"


class AppSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = "Systemix MCP Server"
    environment: str = "development"
    version: str = "0.1.0"


class ServerSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str = "0.0.0.0"
    port: int = 8001
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])


class LoggingSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: str = "INFO"
    format: str = "text"
    access_log: bool = True
    log_request_bodies: bool = False


class AccountSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_tier: str = "standard"
    records: list[AccountRecord] = Field(default_factory=list)


class DatabaseSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    connection_string: str = (
        "postgresql://systemix:systemix@localhost:5432/systemix_kb"
    )
    admin_database: str = "postgres"
    kb_directory: str = "kb"
    seed_on_startup: bool = True


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: AppSettings = Field(default_factory=AppSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    accounts: AccountSettings = Field(default_factory=AccountSettings)
    support: SupportSettingsModel = Field(default_factory=SupportSettingsModel)


def resolve_config_path(config_path: str | Path | None = None) -> Path:
    if config_path is not None:
        return Path(config_path)

    env_config_path = os.getenv(CONFIG_PATH_ENV_VAR)
    if env_config_path:
        return Path(env_config_path)

    repo_root_config = Path(__file__).resolve().parents[2] / DEFAULT_CONFIG_PATH.name
    candidates = [
        Path.cwd() / DEFAULT_CONFIG_PATH.name,
        repo_root_config,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return Path.cwd() / DEFAULT_CONFIG_PATH.name


def load_settings(config_path: str | Path | None = None) -> Settings:
    path = resolve_config_path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file was not found at '{path}'. "
            "Create config.json before starting the server."
        )

    with path.open("r", encoding="utf-8") as handle:
        raw_data: dict[str, Any] = json.load(handle)

    try:
        return Settings.model_validate(raw_data)
    except ValidationError as exc:
        raise ValueError(f"Invalid configuration in '{path}': {exc}") from exc
