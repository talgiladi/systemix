from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from systemix_mcp_server.config import DatabaseSettings, resolve_config_path
from systemix_mcp_server.kb_loader import load_seed_documents, resolve_kb_directory


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KnowledgeBaseBootstrapSummary:
    created_database: bool
    total_documents: int
    seed_directory: Path


class PostgresKnowledgeBaseBootstrapper:
    def __init__(
        self,
        settings: DatabaseSettings,
        config_path: str | Path | None = None,
        connector: Any | None = None,
    ) -> None:
        self._settings = settings
        self._config_path = Path(config_path) if config_path else resolve_config_path()
        self._connector = connector

    def initialize(self) -> KnowledgeBaseBootstrapSummary:
        if not self._settings.seed_on_startup:
            seed_directory = resolve_kb_directory(
                self._settings.kb_directory,
                self._config_path,
            )
            return KnowledgeBaseBootstrapSummary(
                created_database=False,
                total_documents=0,
                seed_directory=seed_directory,
            )

        seed_directory = resolve_kb_directory(
            self._settings.kb_directory,
            self._config_path,
        )
        seed_documents = load_seed_documents(seed_directory)
        database_name = extract_database_name(self._settings.connection_string)
        admin_connection_string = build_admin_connection_string(
            self._settings.connection_string,
            self._settings.admin_database,
        )

        created_database = False
        with self._connect(admin_connection_string, autocommit=True) as admin_connection:
            created_database = ensure_database_exists(admin_connection, database_name)

        with self._connect(self._settings.connection_string) as app_connection:
            ensure_kb_schema(app_connection)
            sync_seed_documents(app_connection, seed_documents)
            app_connection.commit()

        logger.info(
            "Knowledge base bootstrap completed",
            extra={
                "extra_fields": {
                    "created_database": created_database,
                    "database_name": database_name,
                    "seed_directory": str(seed_directory),
                    "seed_document_count": len(seed_documents),
                }
            },
        )
        return KnowledgeBaseBootstrapSummary(
            created_database=created_database,
            total_documents=len(seed_documents),
            seed_directory=seed_directory,
        )

    def _connect(self, connection_string: str, autocommit: bool = False) -> Any:
        if self._connector is not None:
            return self._connector(connection_string, autocommit=autocommit)

        import psycopg

        return psycopg.connect(connection_string, autocommit=autocommit)


def build_admin_connection_string(
    connection_string: str,
    admin_database: str,
) -> str:
    parsed = urlsplit(connection_string)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ValueError(
            "database.connection_string must use a postgres:// or postgresql:// URI."
        )

    admin_path = f"/{admin_database.lstrip('/')}"
    return urlunsplit(
        (parsed.scheme, parsed.netloc, admin_path, parsed.query, parsed.fragment)
    )


def extract_database_name(connection_string: str) -> str:
    parsed = urlsplit(connection_string)
    database_name = parsed.path.lstrip("/")
    if not database_name:
        raise ValueError(
            "database.connection_string must include a target database name."
        )
    return database_name


def ensure_database_exists(connection: Any, database_name: str) -> bool:
    exists = connection.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (database_name,),
    ).fetchone()
    if exists:
        return False

    escaped_name = database_name.replace('"', '""')
    connection.execute(f'CREATE DATABASE "{escaped_name}"')
    return True


def ensure_kb_schema(connection: Any) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS kb_documents (
            id BIGSERIAL PRIMARY KEY,
            doc_id TEXT NOT NULL UNIQUE,
            source_file TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT[] NOT NULL DEFAULT '{}',
            last_updated DATE NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_kb_documents_category
        ON kb_documents (category)
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_kb_documents_tags
        ON kb_documents USING GIN (tags)
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_kb_documents_search
        ON kb_documents
        USING GIN (to_tsvector('english', title || ' ' || content))
        """
    )


def sync_seed_documents(
    connection: Any,
    seed_documents: list[tuple[str, Any]],
) -> None:
    documents_by_file: dict[str, list[Any]] = defaultdict(list)
    for source_file, document in seed_documents:
        documents_by_file[source_file].append(document)

    for source_file, documents in documents_by_file.items():
        connection.execute(
            "DELETE FROM kb_documents WHERE source_file = %s",
            (source_file,),
        )
        for document in documents:
            connection.execute(
                """
                INSERT INTO kb_documents (
                    doc_id,
                    source_file,
                    category,
                    title,
                    content,
                    tags,
                    last_updated
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    document.doc_id,
                    source_file,
                    document.category,
                    document.title,
                    document.content,
                    document.tags,
                    document.last_updated,
                ),
            )
