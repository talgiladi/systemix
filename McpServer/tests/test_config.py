from pathlib import Path

from systemix_mcp_server.config import (
    CONFIG_PATH_ENV_VAR,
    load_settings,
    resolve_config_path,
)


def test_load_settings_supports_project_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
        {
          "app": {
            "name": "Test Server",
            "environment": "test",
            "version": "9.9.9"
          },
          "server": {
            "host": "127.0.0.1",
            "port": 9100,
            "cors_origins": ["http://localhost:3000"]
          },
          "logging": {
            "level": "DEBUG",
            "format": "json",
            "access_log": true,
            "log_request_bodies": true
          },
          "accounts": {
            "default_tier": "gold",
            "records": [
              {
                "user_id": "user-1",
                "account_id": "ACC-1",
                "full_name": "Test User",
                "email": "test@example.com",
                "plan": "enterprise",
                "status": "active",
                "region": "eu-west-1",
                "created_at": "2026-01-01T00:00:00Z",
                "last_login_at": "2026-01-02T00:00:00Z",
                "open_tickets": 0,
                "notes": []
              }
            ]
          },
          "support": {
            "team_name": "Support",
            "default_queue": "general",
            "default_response_sla_hours": 8,
            "issue_routes": {
              "login": {
                "queue": "identity",
                "response_sla_hours": 2,
                "recommended_steps": ["reset session"]
              }
            }
          }
        }
        """.strip(),
        encoding="utf-8",
    )

    settings = load_settings(config_path)

    assert settings.app.name == "Test Server"
    assert settings.server.port == 9100
    assert settings.logging.format == "json"
    assert settings.accounts.records[0].user_id == "user-1"
    assert settings.support.issue_routes["login"].queue == "identity"


def test_resolve_config_path_prefers_current_working_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    resolved = resolve_config_path()

    assert resolved == config_path


def test_resolve_config_path_uses_env_var_when_set(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path = tmp_path / "docker-config.json"
    config_path.write_text("{}", encoding="utf-8")
    monkeypatch.setenv(CONFIG_PATH_ENV_VAR, str(config_path))

    resolved = resolve_config_path()

    assert resolved == config_path
