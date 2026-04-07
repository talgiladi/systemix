from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(
        min_length=1,
        description="The end-user message to process.",
        examples=["Summarize the latest deployment issue."],
    )
    conversation_id: str | None = Field(
        default=None,
        description="Optional client conversation identifier for correlation.",
        examples=["thread-123"],
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary client metadata for future routing and auditing.",
        examples=[{"tenant": "systemix", "channel": "browser-docs"}],
    )


class ToolUsage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    original_name: str
    server_name: str
    status: str
    duration_ms: float
    arguments: dict[str, Any] = Field(default_factory=dict)
    details: dict[str, Any] = Field(default_factory=dict)


class TelemetryData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    latency_ms: float
    active_provider: str
    environment: str
    log_level: str
    prompt_length: int
    discovered_server_count: int
    discovered_tool_count: int
    tool_call_count: int
    llm_rounds: int
    discovery_failures: list[str] = Field(default_factory=list)


class AskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    llm_response: str
    tools_used: list[ToolUsage]
    telemetry: TelemetryData
