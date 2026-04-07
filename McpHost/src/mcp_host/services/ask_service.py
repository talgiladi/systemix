from __future__ import annotations

import logging
from time import perf_counter

from mcp_host.config import Settings
from mcp_host.models.api import AskRequest, AskResponse, TelemetryData, ToolUsage
from mcp_host.models.tooling import ToolCallRequest
from mcp_host.services.llm_service import LlmService
from mcp_host.services.remote_mcp_service import RemoteMcpService


logger = logging.getLogger(__name__)


class AskService:
    """Production-oriented orchestration layer for discovery, LLM routing, and tool execution."""

    def __init__(
        self,
        settings: Settings,
        remote_mcp_service: RemoteMcpService,
        llm_service: LlmService,
    ) -> None:
        self._settings = settings
        self._remote_mcp_service = remote_mcp_service
        self._llm_service = llm_service

    async def ask(self, payload: AskRequest, request_id: str) -> AskResponse:
        start = perf_counter()

        logger.info(
            "Processing ask request",
            extra={
                "request_id": request_id,
                "extra_fields": {
                    "conversation_id": payload.conversation_id,
                    "prompt_length": len(payload.prompt),
                    "metadata_keys": sorted(payload.metadata.keys()),
                },
            },
        )

        discovered_tools, server_results = await self._remote_mcp_service.discover_tools(request_id)
        tool_index = {tool.llm_name: tool for tool in discovered_tools}
        executed_tools: list[ToolUsage] = []

        async def execute_tool(call: ToolCallRequest):
            resolved_tool = tool_index.get(call.tool_name)
            if resolved_tool is None:
                raise LookupError(f"LLM requested unknown tool '{call.tool_name}'")
            result = await self._remote_mcp_service.execute_tool(
                resolved_tool,
                call,
                request_id=request_id,
            )
            executed_tools.append(
                ToolUsage(
                    name=result.llm_name,
                    original_name=result.original_name,
                    server_name=result.server_name,
                    status=result.status,
                    duration_ms=result.duration_ms,
                    arguments=result.arguments,
                    details=result.output,
                )
            )
            return result

        llm_result = await self._llm_service.run_prompt(
            user_query=payload.prompt,
            system_prompt=self._settings.llm.system_prompt,
            discovered_tools=discovered_tools,
            tool_executor=execute_tool,
            request_id=request_id,
        )

        latency_ms = round((perf_counter() - start) * 1000, 3)
        telemetry = TelemetryData(
            request_id=request_id,
            latency_ms=latency_ms,
            active_provider=self._settings.active_provider,
            environment=self._settings.app.environment,
            log_level=self._settings.logging.level.upper(),
            prompt_length=len(payload.prompt),
            discovered_server_count=len(self._settings.mcp_servers),
            discovered_tool_count=len(discovered_tools),
            tool_call_count=len(executed_tools),
            llm_rounds=llm_result.rounds,
            discovery_failures=[
                result.server_name for result in server_results if result.status != "ok"
            ],
        )
        response = AskResponse(
            llm_response=llm_result.final_text,
            tools_used=executed_tools,
            telemetry=telemetry,
        )

        logger.info(
            "Completed ask request",
            extra={
                "request_id": request_id,
                "extra_fields": {
                    "latency_ms": latency_ms,
                    "discovered_tool_count": len(discovered_tools),
                    "tool_call_count": len(response.tools_used),
                    "llm_rounds": llm_result.rounds,
                },
            },
        )
        logger.debug(
            "Ask response payload",
            extra={
                "request_id": request_id,
                "extra_fields": {
                    "response": response.model_dump(mode="json"),
                },
            },
        )
        return response
