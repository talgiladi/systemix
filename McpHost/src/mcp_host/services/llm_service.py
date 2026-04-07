from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable

import httpx

from mcp_host.config import ProviderSettings, Settings
from mcp_host.models.tooling import DiscoveredTool, LlmRunResult, ToolCallRequest, ToolExecutionResult
from mcp_host.services.tool_conversion import convert_tool_to_llm_format


logger = logging.getLogger(__name__)

ToolExecutor = Callable[[ToolCallRequest], Awaitable[ToolExecutionResult]]


class LlmService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._clients = {
            "openai": httpx.AsyncClient(
                base_url=(settings.providers.get("openai") or ProviderSettings()).api_base
                or "https://api.openai.com/v1",
                timeout=settings.llm.request_timeout_seconds,
            ),
            "groq": httpx.AsyncClient(
                base_url=(settings.providers.get("groq") or ProviderSettings()).api_base
                or "https://api.groq.com",
                timeout=settings.llm.request_timeout_seconds,
            ),
            "gemini": httpx.AsyncClient(
                base_url=(settings.providers.get("gemini") or ProviderSettings()).api_base
                or "https://generativelanguage.googleapis.com/v1beta",
                timeout=settings.llm.request_timeout_seconds,
            ),
        }

    async def aclose(self) -> None:
        for client in self._clients.values():
            await client.aclose()

    async def run_prompt(
        self,
        user_query: str,
        system_prompt: str,
        discovered_tools: list[DiscoveredTool],
        tool_executor: ToolExecutor,
        request_id: str,
    ) -> LlmRunResult:
        provider = self._settings.active_provider.lower()
        if provider == "openai":
            return await self._run_openai(user_query, system_prompt, discovered_tools, tool_executor, request_id)
        if provider == "groq":
            return await self._run_groq(user_query, system_prompt, discovered_tools, tool_executor, request_id)
        if provider == "gemini":
            return await self._run_gemini(user_query, system_prompt, discovered_tools, tool_executor, request_id)
        raise ValueError(f"Unsupported active_provider '{self._settings.active_provider}'")

    async def _run_openai(
        self,
        user_query: str,
        system_prompt: str,
        discovered_tools: list[DiscoveredTool],
        tool_executor: ToolExecutor,
        request_id: str,
    ) -> LlmRunResult:
        provider_settings = self._require_provider("openai")
        client = self._clients["openai"]
        tools = [convert_tool_to_llm_format(tool, "openai") for tool in discovered_tools]
        executed_tools: list[ToolExecutionResult] = []
        requested_tool_count = 0

        response = await self._post_json(
            client,
            "/responses",
            headers={"Authorization": f"Bearer {provider_settings.api_key}"},
            payload=self._compact_dict({
                "model": provider_settings.model,
                "temperature": provider_settings.temperature,
                "instructions": system_prompt,
                "input": user_query,
                "tools": tools or None,
            }),
        )

        for round_index in range(1, self._settings.llm.max_tool_rounds + 1):
            tool_calls = self._extract_openai_tool_calls(response)
            if not tool_calls:
                return LlmRunResult(
                    final_text=self._extract_openai_text(response),
                    rounds=round_index,
                    provider_usage=response.get("usage", {}),
                    requested_tool_count=requested_tool_count,
                    executed_tool_results=executed_tools,
                )

            requested_tool_count += len(tool_calls)
            executed = await asyncio.gather(*(tool_executor(call) for call in tool_calls))
            executed_tools.extend(executed)
            response = await self._post_json(
                client,
                "/responses",
                headers={"Authorization": f"Bearer {provider_settings.api_key}"},
                payload=self._compact_dict({
                    "model": provider_settings.model,
                    "temperature": provider_settings.temperature,
                    "previous_response_id": response["id"],
                    "input": [
                        {
                            "type": "function_call_output",
                            "call_id": execution.call_id,
                            "output": json.dumps(execution.output, ensure_ascii=True),
                        }
                        for execution in executed
                    ],
                    "tools": tools or None,
                }),
            )

        raise RuntimeError("OpenAI tool loop exceeded max_tool_rounds")

    async def _run_groq(
        self,
        user_query: str,
        system_prompt: str,
        discovered_tools: list[DiscoveredTool],
        tool_executor: ToolExecutor,
        request_id: str,
    ) -> LlmRunResult:
        del request_id
        provider_settings = self._require_provider("groq")
        client = self._clients["groq"]
        tools = [convert_tool_to_llm_format(tool, "groq") for tool in discovered_tools]
        executed_tools: list[ToolExecutionResult] = []
        requested_tool_count = 0
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]

        for round_index in range(1, self._settings.llm.max_tool_rounds + 1):
            response = await self._post_json(
                client,
                "/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {provider_settings.api_key}"},
                payload=self._compact_dict({
                    "model": provider_settings.model,
                    "temperature": provider_settings.temperature,
                    "messages": messages,
                    "tools": tools or None,
                    "tool_choice": "auto" if tools else "none",
                }),
            )
            choice = response["choices"][0]
            message = choice["message"]
            tool_calls = self._extract_chat_tool_calls(message)
            if not tool_calls:
                return LlmRunResult(
                    final_text=self._extract_chat_text(message),
                    rounds=round_index,
                    provider_usage=response.get("usage", {}),
                    requested_tool_count=requested_tool_count,
                    executed_tool_results=executed_tools,
                )

            requested_tool_count += len(tool_calls)
            assistant_message = self._build_assistant_chat_message(message)
            messages.append(assistant_message)
            executed = await asyncio.gather(*(tool_executor(call) for call in tool_calls))
            executed_tools.extend(executed)
            for execution in executed:
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": execution.call_id,
                        "content": json.dumps(execution.output, ensure_ascii=True),
                    }
                )

        raise RuntimeError("Groq tool loop exceeded max_tool_rounds")

    async def _run_gemini(
        self,
        user_query: str,
        system_prompt: str,
        discovered_tools: list[DiscoveredTool],
        tool_executor: ToolExecutor,
        request_id: str,
    ) -> LlmRunResult:
        del request_id
        provider_settings = self._require_provider("gemini")
        client = self._clients["gemini"]
        declarations = [convert_tool_to_llm_format(tool, "gemini") for tool in discovered_tools]
        executed_tools: list[ToolExecutionResult] = []
        requested_tool_count = 0
        contents: list[dict[str, Any]] = [{"role": "user", "parts": [{"text": user_query}]}]

        for round_index in range(1, self._settings.llm.max_tool_rounds + 1):
            payload = self._compact_dict({
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "contents": contents,
                "generationConfig": {"temperature": provider_settings.temperature},
            })
            if declarations:
                payload["tools"] = [{"functionDeclarations": declarations}]

            response = await self._post_json(
                client,
                f"/models/{provider_settings.model}:generateContent",
                params={"key": provider_settings.api_key},
                payload=payload,
            )
            candidate = response["candidates"][0]
            model_content = candidate.get("content", {})
            tool_calls = self._extract_gemini_tool_calls(model_content)
            if not tool_calls:
                return LlmRunResult(
                    final_text=self._extract_gemini_text(model_content),
                    rounds=round_index,
                    provider_usage=response.get("usageMetadata", {}),
                    requested_tool_count=requested_tool_count,
                    executed_tool_results=executed_tools,
                )

            contents.append(model_content)
            requested_tool_count += len(tool_calls)
            executed = await asyncio.gather(*(tool_executor(call) for call in tool_calls))
            executed_tools.extend(executed)
            for execution in executed:
                contents.append(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": execution.llm_name,
                                    "response": execution.output,
                                }
                            }
                        ],
                    }
                )

        raise RuntimeError("Gemini tool loop exceeded max_tool_rounds")

    def _require_provider(self, provider_name: str) -> ProviderSettings:
        provider = self._settings.providers.get(provider_name)
        if not provider or not provider.api_key or not provider.model:
            raise ValueError(f"Provider '{provider_name}' is missing api_key or model in config.json")
        return provider

    async def _post_json(
        self,
        client: httpx.AsyncClient,
        path: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = await client.post(path, json=payload, headers=headers, params=params)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text
            raise RuntimeError(f"LLM provider request failed: {exc}. Response body: {body}") from exc
        return response.json()

    def _extract_openai_tool_calls(self, response: dict[str, Any]) -> list[ToolCallRequest]:
        calls: list[ToolCallRequest] = []
        for item in response.get("output", []):
            if item.get("type") != "function_call":
                continue
            calls.append(
                ToolCallRequest(
                    call_id=item.get("call_id") or item.get("id") or item["name"],
                    tool_name=item["name"],
                    arguments=self._coerce_arguments(item.get("arguments")),
                )
            )
        return calls

    def _extract_openai_text(self, response: dict[str, Any]) -> str:
        if response.get("output_text"):
            return response["output_text"]

        parts: list[str] = []
        for item in response.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if not isinstance(content, dict):
                    continue
                text = content.get("text")
                if text:
                    parts.append(text)
        return "\n".join(parts).strip()

    def _extract_chat_tool_calls(self, message: dict[str, Any]) -> list[ToolCallRequest]:
        calls: list[ToolCallRequest] = []
        raw_tool_calls = message.get("tool_calls")
        if isinstance(raw_tool_calls, list):
            for tool_call in raw_tool_calls:
                parsed = self._parse_chat_tool_call(tool_call)
                if parsed is not None:
                    calls.append(parsed)

        if calls:
            return calls

        raw_function_call = message.get("function_call")
        if isinstance(raw_function_call, dict):
            parsed = self._parse_function_call_payload(raw_function_call)
            if parsed is not None:
                return [parsed]

        content = message.get("content")
        if isinstance(content, list):
            for part in content:
                if not isinstance(part, dict):
                    continue
                if isinstance(part.get("tool_calls"), list):
                    for tool_call in part["tool_calls"]:
                        parsed = self._parse_chat_tool_call(tool_call)
                        if parsed is not None:
                            calls.append(parsed)
                    continue

                function_call = part.get("function_call") or part.get("functionCall")
                if isinstance(function_call, dict):
                    parsed = self._parse_function_call_payload(function_call)
                    if parsed is not None:
                        calls.append(parsed)

        return calls

    def _parse_chat_tool_call(self, tool_call: Any) -> ToolCallRequest | None:
        if not isinstance(tool_call, dict):
            return None
        function_payload = tool_call.get("function")
        if not isinstance(function_payload, dict):
            return None
        tool_name = function_payload.get("name")
        if not tool_name:
            return None
        return ToolCallRequest(
            call_id=tool_call.get("id") or tool_call.get("call_id") or tool_name,
            tool_name=tool_name,
            arguments=self._coerce_arguments(function_payload.get("arguments")),
        )

    def _parse_function_call_payload(self, function_call: Any) -> ToolCallRequest | None:
        if not isinstance(function_call, dict):
            return None
        tool_name = function_call.get("name")
        if not tool_name:
            return None
        return ToolCallRequest(
            call_id=function_call.get("id") or function_call.get("call_id") or tool_name,
            tool_name=tool_name,
            arguments=self._coerce_arguments(
                function_call.get("arguments") or function_call.get("args")
            ),
        )

    def _build_assistant_chat_message(self, message: dict[str, Any]) -> dict[str, Any]:
        assistant_message: dict[str, Any] = {"role": "assistant"}
        if "content" in message:
            assistant_message["content"] = message.get("content")
        if isinstance(message.get("tool_calls"), list):
            assistant_message["tool_calls"] = message["tool_calls"]
        elif isinstance(message.get("function_call"), dict):
            assistant_message["function_call"] = message["function_call"]
        return assistant_message

    def _extract_chat_text(self, message: dict[str, Any]) -> str:
        content = message.get("content")
        if isinstance(content, str):
            return content
        if not isinstance(content, list):
            return ""

        parts: list[str] = []
        for part in content:
            if not isinstance(part, dict):
                continue
            text = part.get("text")
            if isinstance(text, str) and text:
                parts.append(text)
        return "\n".join(parts).strip()

    def _extract_gemini_tool_calls(self, model_content: dict[str, Any]) -> list[ToolCallRequest]:
        calls: list[ToolCallRequest] = []
        for part in model_content.get("parts", []):
            function_call = part.get("functionCall")
            if not function_call:
                continue
            calls.append(
                ToolCallRequest(
                    call_id=function_call.get("id") or function_call["name"],
                    tool_name=function_call["name"],
                    arguments=function_call.get("args") or {},
                )
            )
        return calls

    def _extract_gemini_text(self, model_content: dict[str, Any]) -> str:
        parts: list[str] = []
        for part in model_content.get("parts", []):
            text = part.get("text")
            if text:
                parts.append(text)
        return "\n".join(parts).strip()

    def _compact_dict(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in payload.items() if value is not None}

    def _coerce_arguments(self, raw_arguments: Any) -> dict[str, Any]:
        if raw_arguments is None:
            return {}
        if isinstance(raw_arguments, dict):
            return raw_arguments
        if isinstance(raw_arguments, str):
            raw_arguments = raw_arguments.strip()
            if not raw_arguments:
                return {}
            return json.loads(raw_arguments)
        raise TypeError(f"Unsupported tool argument payload type: {type(raw_arguments).__name__}")
