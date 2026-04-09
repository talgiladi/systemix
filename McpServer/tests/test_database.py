from __future__ import annotations

from datetime import date

from systemix_mcp_server.database import (
    build_admin_connection_string,
    ensure_database_exists,
    extract_database_name,
    sync_seed_documents,
)
from systemix_mcp_server.models import KnowledgeBaseDocument


class FakeResult:
    def __init__(self, row: tuple[int] | None) -> None:
        self._row = row

    def fetchone(self) -> tuple[int] | None:
        return self._row


class FakeConnection:
    def __init__(self, exists: bool = False) -> None:
        self.exists = exists
        self.commands: list[tuple[str, tuple[object, ...] | None]] = []

    def execute(
        self,
        query: str,
        params: tuple[object, ...] | None = None,
    ) -> FakeResult:
        self.commands.append((query, params))
        if "SELECT 1 FROM pg_database" in query:
            return FakeResult((1,) if self.exists else None)
        return FakeResult(None)


def test_build_admin_connection_string_swaps_database_name() -> None:
    connection_string = "postgresql://systemix:systemix@db:5432/systemix_kb?sslmode=disable"

    admin_connection_string = build_admin_connection_string(
        connection_string,
        admin_database="postgres",
    )

    assert admin_connection_string == (
        "postgresql://systemix:systemix@db:5432/postgres?sslmode=disable"
    )


def test_extract_database_name_returns_target_database() -> None:
    connection_string = "postgresql://systemix:systemix@db:5432/systemix_kb"

    assert extract_database_name(connection_string) == "systemix_kb"


def test_ensure_database_exists_creates_database_only_when_missing() -> None:
    missing_connection = FakeConnection(exists=False)
    existing_connection = FakeConnection(exists=True)

    missing_created = ensure_database_exists(missing_connection, "systemix_kb")
    existing_created = ensure_database_exists(existing_connection, "systemix_kb")

    assert missing_created is True
    assert existing_created is False
    assert any(
        command.startswith('CREATE DATABASE "systemix_kb"')
        for command, _params in missing_connection.commands
    )
    assert not any(
        command.startswith('CREATE DATABASE "systemix_kb"')
        for command, _params in existing_connection.commands
    )


def test_sync_seed_documents_reloads_documents_per_source_file() -> None:
    connection = FakeConnection()
    seed_documents = [
        (
            "payments.txt",
            KnowledgeBaseDocument(
                doc_id="KB_PAY_001",
                title="Accepted cards",
                category="payments",
                content="Accepted cards content",
                tags=["payments"],
                last_updated=date(2026, 3, 1),
            ),
        ),
        (
            "payments.txt",
            KnowledgeBaseDocument(
                doc_id="KB_PAY_002",
                title="Declined payments",
                category="payments",
                content="Declined payments content",
                tags=["payments", "troubleshooting"],
                last_updated=date(2026, 3, 2),
            ),
        ),
    ]

    sync_seed_documents(connection, seed_documents)

    delete_commands = [
        command for command, _params in connection.commands if command.startswith("DELETE")
    ]
    insert_commands = [
        command for command, _params in connection.commands if command.lstrip().startswith("INSERT")
    ]
    assert len(delete_commands) == 1
    assert len(insert_commands) == 2
