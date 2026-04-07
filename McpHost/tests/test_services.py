import asyncio

from mcp_host.config import Settings
from mcp_host.models.api import AskRequest
from mcp_host.models.tooling import (
    DiscoveredTool,
    LlmRunResult,
    ServerDiscoveryResult,
    ToolCallRequest,
    ToolExecutionResult,
)
from mcp_host.services.ask_service import AskService
from mcp_host.services.llm_service import LlmService
from mcp_host.services.remote_mcp_service import RemoteMcpService


def _build_settings(active_provider: str = "groq") -> Settings:
    return Settings.model_validate(
        {
            "app": {
                "name": "Test Host",
                "environment": "test",
                "version": "1.0.0",
            },
            "logging": {
                "level": "debug",
                "format": "text",
                "access_log": False,
                "log_request_bodies": False,
            },
            "llm": {
                "system_prompt": "Use tools when needed.",
                "max_tool_rounds": 4,
                "request_timeout_seconds": 10.0,
            },
            "active_provider": active_provider,
            "providers": {
                "groq": {
                    "api_key": "test-groq-key",
                    "model": "llama-test",
                    "temperature": 0.0,
                },
                "openai": {
                    "api_key": "test-openai-key",
                    "model": "gpt-test",
                    "temperature": 0.0,
                },
                "gemini": {
                    "api_key": "test-gemini-key",
                    "model": "gemini-test",
                    "temperature": 0.0,
                },
            },
            "mcp_servers": [
                {
                    "name": "inventory",
                    "url": "http://localhost:9001/mcp",
                    "description": "Inventory tools",
                    "headers": {},
                    "request_timeout_seconds": 20.0,
                }
            ],
        }
    )


def _build_tool() -> DiscoveredTool:
    return DiscoveredTool(
        llm_name="inventory__lookup_asset",
        original_name="lookup_asset",
        description="Look up an asset.",
        input_schema={
            "type": "object",
            "properties": {"asset_id": {"type": "string"}},
            "required": ["asset_id"],
        },
        server_name="inventory",
        server_url="http://localhost:9001/mcp",
        server_description="Inventory tools",
    )


class _FakeRemoteMcpService:
    async def discover_tools(self, request_id: str):
        del request_id
        return [
            _build_tool()
        ], [
            ServerDiscoveryResult(
                server_name="inventory",
                server_url="http://localhost:9001/mcp",
                status="ok",
                tool_count=1,
            )
        ]

    async def execute_tool(self, tool, call, request_id: str):
        del tool, call, request_id
        raise AssertionError("AskService should build tool usage from llm_result.executed_tool_results")


class _FakeLlmService:
    async def run_prompt(self, **kwargs):
        del kwargs
        return LlmRunResult(
            final_text="server-42 is healthy",
            rounds=2,
            requested_tool_count=1,
            executed_tool_results=[
                ToolExecutionResult(
                    call_id="call-1",
                    llm_name="inventory__lookup_asset",
                    original_name="lookup_asset",
                    server_name="inventory",
                    status="ok",
                    duration_ms=18.3,
                    arguments={"asset_id": "server-42"},
                    output={"content_text": '[{"type":"text","text":"server-42 is healthy"}]'},
                )
            ],
        )


def test_ask_service_telemetry_uses_llm_execution_results() -> None:
    settings = _build_settings(active_provider="openai")
    service = AskService(
        settings=settings,
        remote_mcp_service=_FakeRemoteMcpService(),
        llm_service=_FakeLlmService(),
    )

    response = asyncio.run(
        service.ask(
            AskRequest(prompt="Check server-42"),
            request_id="req-123",
        )
    )

    assert response.tools_used[0].name == "inventory__lookup_asset"
    assert response.telemetry.discovered_tool_count == 1
    assert response.telemetry.tool_call_count == 1
    assert response.telemetry.llm_rounds == 2


def test_groq_tool_loop_counts_rounds_and_records_execution_results() -> None:
    settings = _build_settings(active_provider="groq")
    service = LlmService(settings)
    tool = _build_tool()
    responses = [
        {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "function_call": {
                            "name": "inventory__lookup_asset",
                            "arguments": '{"asset_id":"server-42"}',
                        },
                    }
                }
            ],
            "usage": {"total_tokens": 11},
        },
        {
            "choices": [
                {
                    "message": {
                        "content": [{"type": "text", "text": "server-42 is healthy"}],
                    }
                }
            ],
            "usage": {"total_tokens": 17},
        },
    ]

    async def fake_post_json(*args, **kwargs):
        del args, kwargs
        return responses.pop(0)

    async def tool_executor(call: ToolCallRequest) -> ToolExecutionResult:
        return ToolExecutionResult(
            call_id=call.call_id,
            llm_name=call.tool_name,
            original_name="lookup_asset",
            server_name="inventory",
            status="ok",
            duration_ms=12.4,
            arguments=call.arguments,
            output={"content_text": '[{"type":"text","text":"server-42 is healthy"}]'},
        )

    service._post_json = fake_post_json  # type: ignore[method-assign]
    try:
        result = asyncio.run(
            service.run_prompt(
                user_query="Check server-42",
                system_prompt="Use tools when needed.",
                discovered_tools=[tool],
                tool_executor=tool_executor,
                request_id="req-456",
            )
        )
    finally:
        asyncio.run(service.aclose())

    assert result.final_text == "server-42 is healthy"
    assert result.rounds == 2
    assert result.requested_tool_count == 1
    assert len(result.executed_tool_results) == 1
    assert result.executed_tool_results[0].arguments == {"asset_id": "server-42"}


def test_remote_mcp_service_sets_localhost_host_header_for_host_docker_internal() -> None:
    settings = _build_settings(active_provider="groq")
    settings.mcp_servers[0].url = "http://host.docker.internal:8001/mcp/"
    service = RemoteMcpService(settings)

    headers = service._build_client_headers(settings.mcp_servers[0])

    assert headers["Host"] == "localhost:8001"


def test_ask_service_warns_llm_not_to_claim_tools_when_discovery_fails() -> None:
    settings = _build_settings(active_provider="openai")
    service = AskService(
        settings=settings,
        remote_mcp_service=_FakeRemoteMcpService(),
        llm_service=_FakeLlmService(),
    )

    prompt = service._build_system_prompt(
        base_prompt="Use tools when needed.",
        discovered_tools=[],
        server_results=[
            ServerDiscoveryResult(
                server_name="systemix-support",
                server_url="http://host.docker.internal:8001/mcp/",
                status="error",
                error="Invalid Host header",
            )
        ],
    )

    assert "No MCP tools are available for this request because discovery failed." in prompt
    assert "systemix-support" in prompt
    assert "Do not claim to have queried, called, or used any tool." in prompt
