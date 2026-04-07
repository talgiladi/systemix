# Systemix MCP Host

`Systemix MCP Host` is a Python orchestration service. It is not an MCP server. Its job is to:

1. receive a user request through `POST /api/ask`
2. discover tool metadata from remote MCP servers
3. convert those tools into the configured LLM provider's tool format
4. call the LLM with the system prompt, user query, and remote tool list
5. execute any requested tool calls back against the correct MCP server
6. return the final LLM response, the tools used, and telemetry

## Architecture

This project intentionally follows a host-orchestrator shape:

- No tools are declared locally.
- No local MCP server is mounted.
- Remote MCP sessions are opened only for discovery and tool execution, then closed.
- The host keeps tool metadata for the current request, not long-lived MCP tool sessions.

## Project layout

```text
.
├── openai_config.json
├── pyproject.toml
├── requirements.txt
├── README.md
├── src/
│   └── mcp_host/
│       ├── api/
│       ├── middleware/
│       ├── models/
│       ├── services/
│       ├── app.py
│       ├── config.py
│       ├── logging_config.py
│       └── main.py
└── tests/
```

## Configuration

All runtime configuration lives in `openai_config.json`.

### Main sections

- `app`: service identity and environment
- `server`: API bind settings
- `logging`: console logging behavior
- `llm`: system prompt and tool-loop runtime settings
- `active_provider`: which provider is used at runtime
- `providers`: credentials and model settings per provider
- `mcp_servers`: remote MCP servers to discover tools from

### Example

```json
{
  "app": {
    "name": "Systemix MCP Host",
    "environment": "development",
    "version": "0.1.0"
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "cors_origins": ["*"]
  },
  "logging": {
    "level": "INFO",
    "format": "text",
    "access_log": true,
    "log_request_bodies": false
  },
  "llm": {
    "system_prompt": "You are the Systemix MCP host orchestrator. Use remote MCP tools when they improve accuracy, do not invent tool results, and respond with concise operationally useful answers.",
    "max_tool_rounds": 6,
    "request_timeout_seconds": 60.0
  },
  "active_provider": "groq",
  "providers": {
    "openai": {
      "api_key": "your_openai_api_key_here",
      "model": "gpt-4o-mini",
      "temperature": 0.2,
      "api_base": "https://api.openai.com/v1"
    },
    "groq": {
      "api_key": "your_groq_api_key_here",
      "model": "llama-3.3-70b-versatile",
      "temperature": 0.2,
      "api_base": "https://api.groq.com"
    },
    "gemini": {
      "api_key": "your_google_api_key_here",
      "model": "gemini-2.5-flash",
      "temperature": 0.2
    }
  },
  "mcp_servers": [
    {
      "name": "inventory",
      "url": "http://localhost:9001/mcp",
      "description": "Inventory and asset lookup tools.",
      "headers": {},
      "request_timeout_seconds": 30.0
    }
  ]
}
```

## How `/api/ask` works

1. The host loads the configured system prompt.
2. It opens short-lived connections to each configured MCP server and calls `list_tools`.
3. Each discovered MCP tool is normalized and converted into the active LLM provider's tool schema.
4. The host calls the LLM with:
   - the user prompt
   - the configured system prompt
   - the discovered tool list
5. If the LLM returns tool calls, the host executes them against the correct remote MCP server.
6. Tool results are sent back to the same LLM using that provider's expected tool-result protocol.
7. The loop continues until the LLM returns a final answer or `llm.max_tool_rounds` is reached.

## Tool conversion

The host includes a dedicated conversion function in `src/mcp_host/services/tool_conversion.py`.

It does three important things:

- builds a provider-safe tool name from `server_name + tool_name`
- normalizes JSON Schema for provider compatibility
- converts the MCP tool into the active provider format

Current provider mappings:

- OpenAI Responses API function tools
- Groq chat completions local function tools
- Gemini function declarations

## API

### Interactive docs

When the app is running, open these in a browser:

- `/` redirects to Swagger UI
- `/docs` opens Swagger UI directly
- `/redoc` opens ReDoc

From Swagger UI, expand `POST /api/ask`, click `Try it out`, and submit a JSON body such as:

```json
{
  "prompt": "Summarize the latest deployment issue",
  "conversation_id": "browser-test",
  "metadata": {
    "tenant": "systemix",
    "channel": "swagger"
  }
}
```

### `GET /health`

Returns a lightweight health payload:

```json
{
  "status": "ok",
  "request_id": "9bc8c28d-c61d-49bc-9aa6-4b69a0e4d1ec"
}
```

### `POST /api/ask`

Request:

```json
{
  "prompt": "Summarize the latest deployment issue",
  "conversation_id": "optional-client-thread-id",
  "metadata": {
    "tenant": "systemix"
  }
}
```

Response shape:

```json
{
  "llm_response": "Final answer from the configured provider.",
  "tools_used": [
    {
      "name": "inventory__lookup_asset",
      "original_name": "lookup_asset",
      "server_name": "inventory",
      "status": "ok",
      "duration_ms": 18.3,
      "arguments": {
        "asset_id": "server-42"
      },
      "details": {
        "is_error": false,
        "structured_content": null,
        "content": [
          {
            "type": "text",
            "text": "server-42 is healthy"
          }
        ],
        "content_text": "[{\"type\":\"text\",\"text\":\"server-42 is healthy\"}]"
      }
    }
  ],
  "telemetry": {
    "request_id": "66c12a13-ff8b-4538-8d46-e3028f74d8c0",
    "timestamp": "2026-04-07T10:00:00Z",
    "latency_ms": 182.4,
    "active_provider": "groq",
    "environment": "development",
    "log_level": "INFO",
    "prompt_length": 37,
    "discovered_server_count": 2,
    "discovered_tool_count": 14,
    "tool_call_count": 1,
    "llm_rounds": 2,
    "discovery_failures": []
  }
}
```

## Logging

All logs go to the console.

- `logging.level` controls verbosity
- `logging.format` supports `text` and `json`
- every HTTP request gets an `x-request-id`
- discovery, LLM routing, and tool execution events are logged with request correlation
- request bodies are only logged if `logging.log_request_bodies` is enabled

## Running locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Or:

```bash
pip install -e ".[dev]"
```

Start the API:

```bash
python3 src/mcp_host/main.py
```

Then browse to `http://localhost:8000/` or `http://localhost:8000/docs`.

## Tests

Install test dependencies if needed:

```bash
pip install -e ".[dev]"
```

Then run:

```bash
pytest
```

If `pytest` is not on your shell path, use:

```bash
python3 -m pytest
```

## Important notes

- This host uses the official Python MCP library for remote discovery and tool execution.
- It does not keep long-lived MCP sessions.
- It expects the configured provider API key and model to be valid.
- The current `openai_config.json` should not contain real production secrets in source control. Move live keys to secret storage before deployment.
