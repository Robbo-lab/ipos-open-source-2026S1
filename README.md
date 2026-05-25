#Converter API + MCP

- builds the FastAPI app, wraps it with FastMCP, mounts MCP HTTP/SSE endpoints, registers resources and prompts, and starts uvicorn.
- requirements.txt – Python dependencies.

## Prerequisites

- Python 3.14+
- Virtual environment.
- npm inspector below.

⸻

## Setup from this folder

```bash
python -m venv .venv

# Mac or Gitbash
source .venv/bin/activate

# Windows powershell:
.venv\Scripts\activate
python -m pip install -r requirements.txt

# or use UV:
uv sync
```

⸻

## Run the HTTP + MCP server

```bash
# start the server

# with Python(reommended)
python -m main

# with UV (install in work in progress)
uv run main.py

# with just
just run

```
**To run test curl commands see app/docs/curl_testing/mcp_curl_testing_examples.md**

You’ll see:

- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

MCP endpoints served by FastMCP:

- streamable-http: http://localhost:8003/mcp

Each endpoint returns JSON like:

- { "result": <number>, "operation": "..." } or { "error": "..." } for invalid input.

## Headers & Authentication (common to all)

### Add JSON content type (and optionally your auth token)

-H "Content-Type: application/json" \
-H "Authorization: Bearer <TOKEN>"

Our server doesn’t require auth yet, we can omit the **Authorization** header.

## Use with MCP (VS Code Example)

1. Start the server as above.
2. Point your MCP client to the process.

```json
// Example VS Code .vscode/mcp.json entry:
{
  "servers": {
    "UnitConverter": {
      "command": "python",
      "args": ["main.py"]
    }
  }
}
```

3. From the MCP client, list artifacts. You should see:
   - Tools: celsius_to_fahrenheit, fahrenheit_to_celsius, kilometers_to_miles, miles_to_kilometers
   - Resources: resource://unit_reference, resource://troubleshooting_guide
   - Prompts: explain_conversion, api_usage

⸻

## Inspect with the npm MCP Inspector

- explore everything (tools, resources, prompts) in a browser.
- with the server already running on http://localhost:8003

```bash
# If env error appears
npx @modelcontextprotocol/inspector@latest -e DUMMY=1 --url http://localhost:8003/mcp --transport streamable-http

```

## Handling errors

- Parse error (-32700)
- Invalid request (-32600)
- Method not found (-32601)
- Invalid params (-32602)
- Internal error (-32603)

## Notes

**To run test curl commands see app/docs/curl_testing/mcp_curl_testing_examples.md**

macOS/Linux (bash/zsh)
• The examples above will work as-is.

```bash
# Windows PowerShell
curl -Method POST http://localhost:8003/mcp/ `  -Headers @{ "Content-Type"="application/json" }`
-Body '{"jsonrpc":"2.0","method":"prompts/list","params":{},"id":1}'
```

Windows CMD

```bash
curl -s -X POST http://localhost:8003/mcp/ -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"prompts/list\",\"params\":{},\"id\":1}"
```
