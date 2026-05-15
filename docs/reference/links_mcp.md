1. Core MCP Documentation (Primary References)

These are the most important sources for MCP tools, resources, and prompts.

Model Context Protocol (Official Docs)
• https://modelcontextprotocol.io

Sections particularly relevant to your lesson:

Introduction
• https://modelcontextprotocol.io/docs/introduction

Concepts
• https://modelcontextprotocol.io/docs/concepts

Tools
• https://modelcontextprotocol.io/docs/concepts/tools

Resources
• https://modelcontextprotocol.io/docs/concepts/resources

Prompts
• https://modelcontextprotocol.io/docs/concepts/prompts

Architecture
• https://modelcontextprotocol.io/docs/concepts/architecture

⸻

2. FastMCP / Python Implementation References

Since we are building a Python MCP server, these are very useful.

FastMCP Python Library

GitHub:

https://github.com/modelcontextprotocol/python-sdk

Important sections:

Quickstart
• https://github.com/modelcontextprotocol/python-sdk#quickstart

Creating Tools
• https://github.com/modelcontextprotocol/python-sdk#tools

Resources
• https://github.com/modelcontextprotocol/python-sdk#resources

Prompts
• https://github.com/modelcontextprotocol/python-sdk#prompts

...

⸻

3. MCP Inspector (Testing Tools)

We are already using the browser inspector, so these links help.

MCP Inspector

GitHub

https://github.com/modelcontextprotocol/inspector

Documentation:

https://github.com/modelcontextprotocol/inspector#usage

Command used in our course:

```bash
npx @modelcontextprotocol/inspector python converter_stdio_server.py
```

Inspector allows us to:

• view available tools
• manually call tools
• inspect JSON requests
• debug schemas

⸻

4. JSON Schema Documentation (Important for Tools)

Since tools rely heavily on JSON schema, we need to understand it.

Official docs:

https://json-schema.org/learn/getting-started-step-by-step

Quick reference:

https://json-schema.org/understanding-json-schema/

Useful topics:

• object schemas
• required properties
• enum constraints
• numeric limits

⸻

5. JSON-RPC Protocol (Underlying MCP Calls)

MCP uses JSON-RPC style messaging.

Specification:

https://www.jsonrpc.org/specification

We should understand:

- Field Purpose
- jsonrpc protocol version
- method tool name
- params & arguments
- id request tracking

⸻

6. FastAPI Documentation (Server Layer)

Since your MCP server runs within a Python environment often using FastAPI/ASGI, these references help.

FastAPI docs:

https://fastapi.tiangolo.com

Request handling
• https://fastapi.tiangolo.com/tutorial/body/

Validation with Pydantic
• https://fastapi.tiangolo.com/tutorial/body-model/

Running servers
• https://fastapi.tiangolo.com/deployment/

⸻

7. OpenAI Tool Calling (Conceptual Background)

While MCP is a protocol, tool calling concepts also appear here.

OpenAI docs:

https://platform.openai.com/docs/guides/function-calling

Useful concepts:

• structured tool definitions
• schema-driven inputs
• deterministic tool outputs

⸻

8. Google Cloud Project + Gemini API Setup
   Set up a Google project, create a Gemini API key, and understand current usage limits.

Create and manage Google Cloud projects
• https://cloud.google.com/resource-manager/docs/creating-managing-projects

Gemini API keys in Google AI Studio
• https://ai.google.dev/gemini-api/docs/api-key

Google AI Studio API keys page
• https://aistudio.google.com/app/apikey

Gemini API rate limits
• https://ai.google.dev/gemini-api/docs/rate-limits

Important notes from the current Gemini rate limits documentation:

• Limits are commonly measured as RPM (requests per minute), TPM (tokens per minute), and RPD (requests per day).
• Limits are applied per project, not per API key.
• RPD resets at midnight Pacific time.
• Limits vary by model and quota tier.
• Google recommends checking active limits in AI Studio because they can differ by account and change over time.
