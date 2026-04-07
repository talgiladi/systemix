from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


DEFAULT_CONFIG_PATH = Path("config.json")
LEGACY_CONFIG_PATH = Path("openai_config.json")


class AppSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = "Systemix MCP Host"
    environment: str = "development"
    version: str = "0.1.0"


class ServerSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])


class LoggingSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: str = "INFO"
    format: str = "text"
    access_log: bool = True
    log_request_bodies: bool = False


class LlmSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    system_prompt: str = (
        "You are the Systemix MCP host orchestrator. "
        "Use available tools when they materially improve accuracy, "
        "then produce a concise, correct final answer."
    )
    max_tool_rounds: int = 6
    request_timeout_seconds: float = 60.0


class McpServerSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    url: str
    description: str
    headers: dict[str, str] = Field(default_factory=dict)
    request_timeout_seconds: float = 30.0


class ProviderSettings(BaseModel):
    model_config = ConfigDict(extra="allow")

    api_key: str | None = None
    model: str | None = None
    temperature: float | None = None
    api_base: str | None = None


class EmbeddingProviderSettings(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str | None = None


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: AppSettings = Field(default_factory=AppSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    llm: LlmSettings = Field(default_factory=LlmSettings)
    active_provider: str = "openai"
    providers: dict[str, ProviderSettings] = Field(default_factory=dict)
    embedding_providers: dict[str, EmbeddingProviderSettings] = Field(default_factory=dict)
    mcp_servers: list[McpServerSettings] = Field(default_factory=list)


def resolve_config_path(config_path: str | Path | None = None) -> Path:
    if config_path is not None:
        return Path(config_path)

    repo_root = Path(__file__).resolve().parents[2]
    repo_root_config = repo_root / DEFAULT_CONFIG_PATH.name
    repo_root_legacy_config = repo_root / LEGACY_CONFIG_PATH.name
    candidates = [
        Path.cwd() / DEFAULT_CONFIG_PATH.name,
        repo_root_config,
        Path.cwd() / LEGACY_CONFIG_PATH.name,
        repo_root_legacy_config,
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
            "Create config.json before starting the host."
        )

    with path.open("r", encoding="utf-8") as handle:
        raw_data: dict[str, Any] = json.load(handle)

    try:
        return Settings.model_validate(raw_data)
    except ValidationError as exc:
        raise ValueError(f"Invalid configuration in '{path}': {exc}") from exc
