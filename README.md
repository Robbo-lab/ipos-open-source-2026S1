#Converter API + MCP

- builds the FastAPI app, wraps it with FastMCP, mounts MCP HTTP/SSE endpoints, registers resources and prompts, and starts uvicorn.
- requirements.txt – Python dependencies.

## Prerequisites

- Python 3.10+ (tested with 3.12).
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
```

⸻

## Run the HTTP + MCP server

```bash
# start the server

python -m main

```

You’ll see:

- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

MCP endpoints served by FastMCP:

- streamable-http: http://localhost:8003/mcp
- SSE: http://localhost:8003/sse

⸻

## Try the HTTP endpoints (curl)

```bash
curl -X POST "http://localhost:8003/miles-to-kilometers?miles=3.1" \
 -H "Authorization: Bearer 143f4a46d74fee0d7918b2857577868cb3daf9e6e50ee91c2f7975ba26fdb8f7"

# If we use pydantic models
curl -X POST "http://localhost:8003/miles-to-kilometers" \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer Y658139cf61948208ed76a4b36122b9552ec5c3f6da5e02f7c5d85d995dede17dE" \
 -d "3.1"
```

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

## JSON-RPC Examples for Prompts & Resources

1. List all prompts

```bash
curl -s -X POST <SERVER_URL> \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"prompts/list","params":{},"id":1}'
```

⸻

2. Get a specific prompt

```bash
curl -s -X POST <SERVER_URL> \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"prompts/get","params":{"name":"summarize"},"id":2}'
```

⸻

3. Render/execute a prompt with variables

```bash
curl -s -X POST <SERVER_URL> \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"prompts/render","params":{"name":"summarize","variables":{"text":"This is the content to summarize","tone":"neutral"}},"id":3}'
```

4. List available resources

```bash
curl -s -X POST <SERVER_URL> \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"resources/list","params":{},"id":4}'
```

5. Read a resource by URI

```bash
curl -s -X POST <SERVER_URL> \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"resources/read","params":{"uri":"file:///data/report.pdf"},"id":5}'
```

6. Search resources (if supported)

```bash
curl -s -X POST <SERVER_URL> \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"resources/search","params":{"query":"error OR exception","limit":50},"id":6}'
```

⸻

## Handling errors

- Parse error (-32700)
- Invalid request (-32600)
- Method not found (-32601)
- Invalid params (-32602)
- Internal error (-32603)

## Notes

macOS/Linux (bash/zsh)
• The examples above will work as-is.

```bash
# Windows PowerShell
curl -Method POST <SERVER_URL> `  -Headers @{ "Content-Type"="application/json" }`
-Body '{"jsonrpc":"2.0","method":"prompts/list","params":{},"id":1}'
```

Windows CMD

```bash
curl -s -X POST <SERVER_URL> -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"prompts/list\",\"params\":{},\"id\":1}"
```
