from __future__ import annotations

import json
import logging
from time import perf_counter
from typing import Any
from urllib.parse import urlparse

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import CallToolResult, EmbeddedResource, ImageContent, TextContent

from mcp_host.config import McpServerSettings, Settings
from mcp_host.models.tooling import (
    DiscoveredTool,
    ServerDiscoveryResult,
    ToolCallRequest,
    ToolExecutionResult,
)
from mcp_host.services.tool_conversion import build_llm_tool_name, normalize_json_schema


logger = logging.getLogger(__name__)


class RemoteMcpService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def discover_tools(
        self,
        request_id: str,
    ) -> tuple[list[DiscoveredTool], list[ServerDiscoveryResult]]:
        discovered: list[DiscoveredTool] = []
        server_results: list[ServerDiscoveryResult] = []

        for server in self._settings.mcp_servers:
            try:
                tools = await self._discover_server_tools(server)
                discovered.extend(tools)
                server_results.append(
                    ServerDiscoveryResult(
                        server_name=server.name,
                        server_url=server.url,
                        status="ok",
                        tool_count=len(tools),
                    )
                )
                logger.info(
                    "Discovered MCP tools",
                    extra={
                        "request_id": request_id,
                        "extra_fields": {
                            "server_name": server.name,
                            "server_url": server.url,
                            "tool_count": len(tools),
                        },
                    },
                )
            except Exception as exc:
                server_results.append(
                    ServerDiscoveryResult(
                        server_name=server.name,
                        server_url=server.url,
                        status="error",
                        error=str(exc),
                    )
                )
                logger.warning(
                    "Failed MCP tool discovery",
                    extra={
                        "request_id": request_id,
                        "extra_fields": {
                            "server_name": server.name,
                            "server_url": server.url,
                            "error": str(exc),
                        },
                    },
                )

        return discovered, server_results

    async def execute_tool(
        self,
        tool: DiscoveredTool,
        call: ToolCallRequest,
        request_id: str,
    ) -> ToolExecutionResult:
        server_config = self._find_server(tool.server_name)
        started = perf_counter()
        try:
            async with httpx.AsyncClient(
                headers=self._build_client_headers(server_config),
                timeout=server_config.request_timeout_seconds,
            ) as http_client:
                async with streamable_http_client(tool.server_url, http_client=http_client) as (
                    read_stream,
                    write_stream,
                    _,
                ):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        result = await session.call_tool(
                            tool.original_name,
                            arguments=call.arguments,
                        )
        except Exception as exc:
            duration_ms = round((perf_counter() - started) * 1000, 3)
            logger.exception(
                "Remote tool execution failed",
                extra={
                    "request_id": request_id,
                    "extra_fields": {
                        "server_name": tool.server_name,
                        "tool_name": tool.original_name,
                        "llm_tool_name": tool.llm_name,
                    },
                },
            )
            return ToolExecutionResult(
                call_id=call.call_id,
                llm_name=tool.llm_name,
                original_name=tool.original_name,
                server_name=tool.server_name,
                status="error",
                duration_ms=duration_ms,
                arguments=call.arguments,
                output={"error": str(exc)},
                is_error=True,
            )

        duration_ms = round((perf_counter() - started) * 1000, 3)
        serialized = self._serialize_tool_result(result)
        status = "error" if result.isError else "ok"
        logger.info(
            "Executed remote MCP tool",
            extra={
                "request_id": request_id,
                "extra_fields": {
                    "server_name": tool.server_name,
                    "tool_name": tool.original_name,
                    "llm_tool_name": tool.llm_name,
                    "status": status,
                    "duration_ms": duration_ms,
                },
            },
        )
        return ToolExecutionResult(
            call_id=call.call_id,
            llm_name=tool.llm_name,
            original_name=tool.original_name,
            server_name=tool.server_name,
            status=status,
            duration_ms=duration_ms,
            arguments=call.arguments,
            output=serialized,
            is_error=result.isError,
        )

    async def _discover_server_tools(self, server: McpServerSettings) -> list[DiscoveredTool]:
        async with httpx.AsyncClient(
            headers=self._build_client_headers(server),
            timeout=server.request_timeout_seconds,
        ) as http_client:
            async with streamable_http_client(server.url, http_client=http_client) as (
                read_stream,
                write_stream,
                _,
            ):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    tools: list[DiscoveredTool] = []
                    cursor: str | None = None

                    while True:
                        response = await session.list_tools(cursor=cursor)
                        for tool in response.tools:
                            tools.append(
                                DiscoveredTool(
                                    llm_name=build_llm_tool_name(server.name, tool.name),
                                    original_name=tool.name,
                                    title=tool.title,
                                    description=tool.description or "Remote MCP tool",
                                    input_schema=normalize_json_schema(tool.inputSchema),
                                    output_schema=tool.outputSchema,
                                    server_name=server.name,
                                    server_url=server.url,
                                    server_description=server.description,
                                )
                            )
                        cursor = response.nextCursor
                        if not cursor:
                            return tools

    def _find_server(self, server_name: str) -> McpServerSettings:
        for server in self._settings.mcp_servers:
            if server.name == server_name:
                return server
        raise LookupError(f"Configured MCP server '{server_name}' was not found")

    def _build_client_headers(self, server: McpServerSettings) -> dict[str, str]:
        headers = dict(server.headers)
        if any(key.lower() == "host" for key in headers):
            return headers

        parsed = urlparse(server.url)
        if parsed.hostname == "host.docker.internal":
            port = parsed.port
            headers["Host"] = f"localhost:{port}" if port is not None else "localhost"
        return headers

    def _serialize_tool_result(self, result: CallToolResult) -> dict[str, Any]:
        contents: list[dict[str, Any]] = []
        for item in result.content:
            if isinstance(item, TextContent):
                contents.append({"type": "text", "text": item.text})
            elif isinstance(item, ImageContent):
                contents.append(
                    {
                        "type": "image",
                        "mime_type": item.mimeType,
                        "note": "Binary image content omitted from LLM payload.",
                    }
                )
            elif isinstance(item, EmbeddedResource):
                resource = item.resource.model_dump(mode="json")
                contents.append({"type": "resource", "resource": resource})
            else:
                contents.append({"type": item.type, "value": item.model_dump(mode="json")})

        output = {
            "is_error": result.isError,
            "structured_content": result.structuredContent,
            "content": contents,
        }
        output["content_text"] = json.dumps(contents, ensure_ascii=True)
        return output
