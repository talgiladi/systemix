from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class DiscoveredTool(BaseModel):
    model_config = ConfigDict(extra="forbid")

    llm_name: str
    original_name: str
    title: str | None = None
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None
    server_name: str
    server_url: str
    server_description: str


class ServerDiscoveryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    server_name: str
    server_url: str
    status: str
    tool_count: int = 0
    error: str | None = None


class ToolCallRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    call_id: str = Field(default_factory=lambda: str(uuid4()))
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    call_id: str
    llm_name: str
    original_name: str
    server_name: str
    status: str
    duration_ms: float
    arguments: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    is_error: bool = False


class LlmRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    final_text: str
    rounds: int
    provider_usage: dict[str, Any] = Field(default_factory=dict)
    requested_tool_count: int = 0
    executed_tool_results: list[ToolExecutionResult] = Field(default_factory=list)
