from pathlib import Path

from mcp_host.config import load_settings, resolve_config_path


def test_load_settings_supports_extended_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
        {
          "app": {
            "name": "Test Host",
            "environment": "test",
            "version": "1.2.3"
          },
          "server": {
            "host": "127.0.0.1",
            "port": 9001,
            "cors_origins": ["http://localhost:3000"]
          },
          "logging": {
            "level": "DEBUG",
            "format": "json",
            "access_log": true,
            "log_request_bodies": false
          },
          "llm": {
            "system_prompt": "Use tools carefully.",
            "max_tool_rounds": 4,
            "request_timeout_seconds": 45.0
          },
          "active_provider": "openai",
          "providers": {
            "openai": {
              "api_key": "test",
              "model": "demo-model",
              "temperature": 0.0
            }
          }, 
          "mcp_servers": [
            {
              "name": "inventory",
              "url": "http://localhost:9001/mcp",
              "description": "Inventory tools",
              "headers": {},
              "request_timeout_seconds": 20.0
            }
          ],
          "embedding_providers": {}
        }
        """.strip(),
        encoding="utf-8",
    )

    settings = load_settings(config_path)

    assert settings.app.name == "Test Host"
    assert settings.server.port == 9001
    assert settings.logging.format == "json"
    assert settings.llm.max_tool_rounds == 4
    assert settings.mcp_servers[0].name == "inventory"


def test_resolve_config_path_prefers_current_working_directory(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    resolved = resolve_config_path()

    assert resolved == config_path


def test_resolve_config_path_falls_back_to_legacy_name(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "openai_config.json"
    config_path.write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    resolved = resolve_config_path()

    assert resolved == config_path
