import asyncio
from types import SimpleNamespace

from mcp_host.api.routes import ask, docs_redirect, healthcheck
from mcp_host.models.api import AskRequest, AskResponse, TelemetryData, ToolUsage


class FakeAskService:
    async def ask(self, payload, request_id: str) -> AskResponse:
        return AskResponse(
            llm_response=f"Echo: {payload.prompt}",
            tools_used=[
                ToolUsage(
                    name="inventory__lookup_asset",
                    original_name="lookup_asset",
                    server_name="inventory",
                    status="ok",
                    duration_ms=12.5,
                    arguments={"asset_id": "abc"},
                    details={"content_text": '[{"type":"text","text":"ok"}]'},
                )
            ],
            telemetry=TelemetryData(
                request_id=request_id,
                latency_ms=18.2,
                active_provider="openai",
                environment="test",
                log_level="DEBUG",
                prompt_length=len(payload.prompt),
                discovered_server_count=1,
                discovered_tool_count=3,
                tool_call_count=1,
                llm_rounds=2,
            ),
        )


def test_healthcheck_returns_ok() -> None:
    request = SimpleNamespace(state=SimpleNamespace(request_id="req-123"))

    payload = asyncio.run(healthcheck(request))

    assert payload["status"] == "ok"
    assert payload["request_id"] == "req-123"


def test_docs_redirect_points_to_swagger_ui() -> None:
    response = asyncio.run(docs_redirect())

    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_ask_route_returns_expected_contract() -> None:
    request = SimpleNamespace(
        state=SimpleNamespace(request_id="req-456"),
        app=SimpleNamespace(
            state=SimpleNamespace(
                settings=SimpleNamespace(
                    logging=SimpleNamespace(log_request_bodies=False),
                )
            )
        ),
    )
    payload = AskRequest(
        prompt="What tools are available?",
        metadata={"channel": "test"},
    )

    response = asyncio.run(ask(payload, request, ask_service=FakeAskService()))

    assert response.llm_response == "Echo: What tools are available?"
    assert response.tools_used[0].name == "inventory__lookup_asset"
    assert response.telemetry.tool_call_count == 1
    assert response.telemetry.request_id == "req-456"
