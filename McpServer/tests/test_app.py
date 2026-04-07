import asyncio
import logging
import json
from types import SimpleNamespace

from systemix_mcp_server.app import browser_test_page, create_app, docs_redirect, healthcheck
from systemix_mcp_server.config import LoggingSettings, Settings
from systemix_mcp_server.logging_config import configure_logging
from systemix_mcp_server.middleware import _extract_mcp_log_entry


def build_settings() -> Settings:
    return Settings.model_validate(
        {
            "logging": {
                "level": "DEBUG",
                "format": "text",
                "access_log": True,
                "log_request_bodies": False,
            },
            "accounts": {
                "records": [
                    {
                        "user_id": "user-1001",
                        "account_id": "ACC-1001",
                        "full_name": "Dana Levi",
                        "email": "dana@example.com",
                        "plan": "enterprise",
                        "status": "active",
                        "region": "eu-west-1",
                        "created_at": "2024-02-15T10:30:00Z",
                        "last_login_at": "2026-04-06T17:25:00Z",
                        "open_tickets": 1,
                        "notes": ["Primary billing owner"]
                    }
                ]
            },
            "support": {
                "issue_routes": {
                    "login": {
                        "queue": "identity-support",
                        "response_sla_hours": 2,
                        "recommended_steps": ["Check SSO configuration"]
                    }
                }
            }
        }
    )


def test_healthcheck_returns_ok() -> None:
    request = SimpleNamespace(state=SimpleNamespace(request_id="req-123"))

    payload = asyncio.run(healthcheck(request))

    assert payload["status"] == "ok"
    assert payload["request_id"] == "req-123"


def test_root_redirects_to_browser() -> None:
    response = asyncio.run(docs_redirect())

    assert response.status_code == 307
    assert response.headers["location"] == "/browser"


def test_browser_page_is_served() -> None:
    response = asyncio.run(browser_test_page())

    assert response.status_code == 200
    assert "Systemix MCP Browser Test" in response.body.decode("utf-8")


def test_app_registers_expected_routes() -> None:
    app = create_app(build_settings(), include_mcp_server=False)
    route_paths = {route.path for route in app.routes}

    assert "/" in route_paths
    assert "/health" in route_paths
    assert "/browser" in route_paths


def test_extract_mcp_tool_call_log_entry_includes_details() -> None:
    entry = _extract_mcp_log_entry(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": "tool-call-1",
                "method": "tools/call",
                "params": {
                    "name": "get_technical_support",
                    "arguments": {
                        "user_id": "user-1001",
                        "issue_type": "login",
                        "summary": "User reports repeated login failures after SSO redirect.",
                        "severity": "high",
                    },
                },
            }
        )
    )

    assert entry is not None
    message, fields = entry
    assert message == "MCP tool call"
    assert fields["tool_name"] == "get_technical_support"
    assert fields["tool_arguments"]["user_id"] == "user-1001"
    assert fields["tool_arguments"]["severity"] == "high"


def test_configure_logging_sets_uvicorn_and_mcp_loggers_to_requested_level() -> None:
    configure_logging(LoggingSettings(level="DEBUG", format="text"))

    assert logging.getLogger("systemix_mcp_server").getEffectiveLevel() == logging.DEBUG
    assert logging.getLogger("mcp.server.lowlevel.server").getEffectiveLevel() == logging.DEBUG
    assert logging.getLogger("uvicorn.access").getEffectiveLevel() == logging.DEBUG
