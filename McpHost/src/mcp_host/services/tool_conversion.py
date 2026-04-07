from __future__ import annotations

import hashlib
import re
from copy import deepcopy
from typing import Any

from mcp_host.models.tooling import DiscoveredTool


TOOL_NAME_LIMIT = 64


def build_llm_tool_name(server_name: str, original_name: str) -> str:
    left = re.sub(r"[^a-z0-9_]", "_", server_name.lower())
    right = re.sub(r"[^a-z0-9_]", "_", original_name.lower())
    left = re.sub(r"_+", "_", left).strip("_") or "server"
    right = re.sub(r"_+", "_", right).strip("_") or "tool"
    normalized = f"{left}__{right}"
    if len(normalized) <= TOOL_NAME_LIMIT:
        return normalized

    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:10]
    prefix = normalized[: TOOL_NAME_LIMIT - 11].rstrip("_")
    return f"{prefix}_{digest}"


def normalize_json_schema(schema: dict[str, Any] | None) -> dict[str, Any]:
    if not schema:
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

    normalized = deepcopy(schema)
    _normalize_schema_node(normalized)
    return normalized


def _normalize_schema_node(node: dict[str, Any]) -> None:
    for composite_key in ("oneOf", "anyOf", "allOf"):
        variants = node.get(composite_key)
        if isinstance(variants, list):
            for variant in variants:
                if isinstance(variant, dict):
                    _normalize_schema_node(variant)

    if node.get("type") == "object" or "properties" in node:
        properties = node.setdefault("properties", {})
        if isinstance(properties, dict):
            for child in properties.values():
                if isinstance(child, dict):
                    _normalize_schema_node(child)
        node.setdefault("required", [])
        node.setdefault("additionalProperties", False)

    items = node.get("items")
    if isinstance(items, dict):
        _normalize_schema_node(items)


def build_tool_description(tool: DiscoveredTool) -> str:
    title = tool.title or tool.original_name
    return (
        f"{tool.description} "
        f"(Server: {tool.server_name}. Remote tool name: {title}.)"
    ).strip()


def convert_tool_to_llm_format(tool: DiscoveredTool, provider: str) -> dict[str, Any]:
    schema = normalize_json_schema(tool.input_schema)
    description = build_tool_description(tool)

    if provider == "openai":
        return {
            "type": "function",
            "name": tool.llm_name,
            "description": description,
            "parameters": schema,
            "strict": True,
        }

    if provider == "groq":
        return {
            "type": "function",
            "function": {
                "name": tool.llm_name,
                "description": description,
                "parameters": schema,
            },
        }

    if provider == "gemini":
        return {
            "name": tool.llm_name,
            "description": description,
            "parameters": schema,
        }

    raise ValueError(f"Unsupported provider '{provider}'")
