import json

import pytest

from systemix_mcp_server.config import Settings
from systemix_mcp_server.services import AccountNotFoundError, SystemixMcpService


@pytest.fixture()
def service() -> SystemixMcpService:
    settings = Settings.model_validate(
        {
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
                "team_name": "Systemix Technical Support",
                "default_queue": "general-support",
                "default_response_sla_hours": 8,
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
    return SystemixMcpService(settings)


def test_get_account_details_returns_expected_payload(service: SystemixMcpService) -> None:
    payload = service.get_account_details("user-1001")

    assert payload["account_id"] == "ACC-1001"
    assert payload["plan"] == "enterprise"
    assert payload["open_tickets"] == 1


def test_get_account_details_requires_existing_user(service: SystemixMcpService) -> None:
    with pytest.raises(AccountNotFoundError):
        service.get_account_details("missing-user")


def test_get_technical_support_uses_issue_route(service: SystemixMcpService) -> None:
    payload = service.get_technical_support(
        user_id="user-1001",
        issue_type="login",
        summary="SSO loop",
        severity="high",
    )

    assert payload["assigned_queue"] == "identity-support"
    assert payload["response_sla_hours"] == 2
    assert payload["severity"] == "high"


def test_build_support_prompt_includes_user_id(service: SystemixMcpService) -> None:
    prompt = service.build_support_prompt(
        user_id="user-1001",
        issue_summary="Investigate access issue",
        preferred_tone="formal",
    )

    assert "user-1001" in prompt
    assert "formal tone" in prompt
    assert "Investigate access issue" in prompt


def test_get_account_resource_returns_json(service: SystemixMcpService) -> None:
    payload = json.loads(service.get_account_resource("user-1001"))

    assert payload["kind"] == "account_profile"
    assert payload["user_id"] == "user-1001"
