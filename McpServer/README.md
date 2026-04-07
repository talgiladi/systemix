# Systemix MCP Server

`Systemix MCP Server` is a Python MCP server built with the `mcp` library. It exposes:

- 2 tools:
  - `get_account_details`
  - `get_technical_support`
- 1 prompt:
  - `technical_support_prompt`
- 1 resource template:
  - `account://{user_id}/profile`

Every callable surface requires `user_id`, either as a tool argument, a prompt argument, or as part of the resource URI.

## Project Layout

```text
.
├── config.example.json
├── pyproject.toml
├── requirements.txt
├── README.md
├── src/
│   └── systemix_mcp_server/
│       ├── browser/
│       │   └── index.html
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       ├── logging_config.py
│       ├── main.py
│       ├── mcp_server.py
│       ├── middleware.py
│       ├── models.py
│       └── services.py
└── tests/
    ├── conftest.py
    ├── test_app.py
    ├── test_config.py
    └── test_services.py
```

## Configuration

The runtime configuration lives in `config.json`, matching the config-file pattern used by `../McpHost`.

`config.json` is intentionally gitignored because it may contain secrets such as API keys. The committed reference file is `config.example.json`, which documents the required structure with safe placeholder or sample values.

Create your local runtime config by copying the example:

```bash
cp config.example.json config.json
```

When running in Docker, the container can read the mounted config file through `SYSTEMIX_MCP_SERVER_CONFIG_PATH=/app/config.json`.

If you add, remove, or rename any configuration field, update `config.example.json` in the same change. This is a required maintenance step for both human contributors and LLM code agents so the documented structure never drifts from the real config schema.

Main sections:

- `app`: service identity
- `server`: bind host, port, and browser CORS settings
- `logging`: level, formatter, access logs, and request body logging
- `accounts`: sample account data returned by the server
- `support`: support routing and troubleshooting defaults

The log level is controlled through `logging.level`.

## Running

Install dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Start the server:

```bash
python3 -m systemix_mcp_server.main
```

Or:

```bash
systemix-mcp-server
```

The app starts on `http://localhost:8001` by default.

## Running with Docker

Build the image:

```bash
docker build -t systemix-mcp-server .
```

Run the container with your local runtime config mounted read-only:

```bash
docker run --rm \
  --name systemix-mcp-server \
  -p 8001:8001 \
  -e SYSTEMIX_MCP_SERVER_CONFIG_PATH=/app/config.json \
  -v "$(pwd)/config.json:/app/config.json:ro" \
  --add-host=host.docker.internal:host-gateway \
  systemix-mcp-server
```

Then open `http://localhost:8001/browser`.

### Docker Compose

This repo includes `compose.yml`, so the server can be started out of the box with the local `config.json` mounted into the container:

```bash
docker compose up --build
```

The compose service:

- publishes container port `8001` to host port `8001`
- mounts `./config.json` into `/app/config.json` as read-only
- sets `SYSTEMIX_MCP_SERVER_CONFIG_PATH=/app/config.json`
- adds `host.docker.internal` so the container can reach services running on your host machine if needed

Stop it with:

```bash
docker compose down
```

## Endpoints

- `/health`: lightweight HTTP health check
- `/browser`: browser-based MCP test harness
- `/mcp/`: Streamable HTTP MCP endpoint

The browser page is intended for manual smoke testing without writing code. It lets you:

1. initialize an MCP session
2. list tools, prompts, and resources
3. call either tool with a `user_id`
4. fetch the prompt with a `user_id`
5. read the resource with a `user_id`

## Browser Testing

1. Start the server.
2. Open `http://localhost:8001/browser`.
3. Click `Initialize`.
4. Use the forms to call tools, fetch the prompt, and read the resource.

This exercises the real MCP endpoint over HTTP from a browser.

If you run the server inside Docker, the browser test page is still available at `http://localhost:8001/browser` on the host because compose publishes port `8001`.

## Unit Tests

Run the test suite with:

```bash
pytest
```
