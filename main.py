# Unit Converter API + MCP (tools, resources, prompts)
# Uses FastAPI for HTTP routes and FastMCP to expose tools/resources/prompts over HTTP/SSE transports.

# Create Database

from fastapi import APIRouter, FastAPI
from fastmcp import FastMCP

from app.mcp.mcp_prompts.converter_prompts import explain_conversion_prompt
from app.mcp.mcp_resources.converter_resources import RESOURCE_DEFINITIONS
from app.mcp.mcp_tools.miles_to_km import router as mile_to_km
from app.routes.router_handler import Router
from app.utils.resource_utils import register_resources
from app.security.rate_limit import RateLimitMiddleware

# FastAPI app for plain HTTP
app = FastAPI(
    title="Unit Converter MCP Server",
    description="FastAPI endpoints auto-exposed as MCP tools via FastMCP, with resources and prompts.",
    version="1.2.1",
)

# --- Rate Limiting ---
app.add_middleware(RateLimitMiddleware)

# --- Register Tool ---
app.include_router(mile_to_km)

# --- Register System ---
system_router = APIRouter(prefix="", tags=["system"])
task_router = APIRouter(prefix="", tags=["task"])

Router.load_all_routes()
Router.add_routes_to_app(app)


# FastMCP server generated from FastAPI OpenAPI (tools) plus manual resources/prompts
mcp = FastMCP.from_fastapi(
    app,
    name="Unit Converter MCP Server",
    instructions="Unit conversion tools with supporting resources and prompts.",
)

# --- Register Resources --- dynamically via URI template
register_resources(mcp, RESOURCE_DEFINITIONS)


# Prompts
@mcp.prompt(
    name="explain_conversion",
    description="Guide a learner through the math for a conversion.",
)
def _prompt_explain_conversion(input_value: str, input_unit: str, target_unit: str):
    return explain_conversion_prompt(
        input_value=input_value,
        input_unit=input_unit,
        target_unit=target_unit,
    )


# Build MCP sub-application and mount onto FastAPI
mcp_http_app = mcp.http_app(path="/", transport="streamable-http")

# Ensure FastAPI runs the MCP lifespan so streamable-http initialises properly
app.router.lifespan_context = mcp_http_app.lifespan

app.mount("/mcp", mcp_http_app)

if __name__ == "__main__":
    import uvicorn

    PORT = 8003

    print(
        "Starting the Unit Converter API server (HTTP + MCP tools/resources/prompts)..."
    )
    print(f"HTTP docs:      http://localhost:{PORT}/docs")
    print(f"HTTP redoc:     http://localhost:{PORT}/redoc")
    print(f"MCP endpoint:   http://localhost:{PORT}/mcp (HTTP)")

    uvicorn.run(
        app,
        host="localhost",
        port=PORT,
        log_level="trace",  # Uvicorn internal logging
    )
