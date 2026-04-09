from __future__ import annotations

import json
from pathlib import Path

from systemix_mcp_server.models import KnowledgeBaseDocument


SEED_SOURCE_FILES = (
    "account_and_login.txt",
    "payments.txt",
    "product_usage.txt",
    "shipping_and_orders.txt",
    "returns_and_refunds.txt",
)


def resolve_kb_directory(raw_directory: str | Path, config_path: Path) -> Path:
    directory = Path(raw_directory)
    if directory.is_absolute():
        return directory

    candidates = (
        config_path.parent / directory,
        Path.cwd() / directory,
        Path(__file__).resolve().parents[2] / directory,
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


def load_seed_documents(seed_directory: Path) -> list[tuple[str, KnowledgeBaseDocument]]:
    documents: list[tuple[str, KnowledgeBaseDocument]] = []
    for filename in SEED_SOURCE_FILES:
        file_path = seed_directory / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Seed file was not found at '{file_path}'.")

        for raw_line in file_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            payload = json.loads(line)
            documents.append((filename, KnowledgeBaseDocument.model_validate(payload)))

    return documents
