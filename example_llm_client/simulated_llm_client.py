from __future__ import annotations

import asyncio
import os
import time
from typing import Any

from dotenv import load_dotenv
from fastmcp import Client

from mcp_prompts.converter_prompts import explain_conversion_prompt

load_dotenv()

LLM_API_KEY = "api_key"
LL_MODEL = "llm_model"
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8003/mcp")

KM_TO_MILES_TOOL = "kilometers_to_miles"


def require_env(value: str | None, name: str) -> str:
    pass


async def handle_mcp_progress() -> None:
    """Print MCP progress notifications so they are visible during the demo."""
    pass


async def call_mcp_tool():
    """
    Send an MCP request to the existing converter MCP server and return its response.

    The calculation happens on the MCP server. This client only orchestrates the
    request/response flow and forwards the structured tool result to Gemini.
    """

    pass


def build_gemini_prompt():
    """
    Build the model-side context sent to Gemini.

    This reuses the existing explain_conversion_prompt helper so the LLM
    client follows the same teaching prompt pattern as the MCP prompt module.
    LLM receives the verified MCP response after the tool call completes.
    LLM explains the result, but it is not asked to perform the calculation.
    """
    pass


def generate_ll_explanation(
) -> str:
    """Check fro streamable content from LLM output and return the combined explanation text."""

    pass


async def run() -> None:
    """
    Run the LLM + MCP integration demo.

    Workflow:
    1. Send a request to the MCP server at MCP_SERVER_URL.
    2. Receive a structured MCP tool result back into this client.
    3. Send that result to Gemini for explanation only.
    """


def main() -> None:
    # Leave as asynchorous
    asyncio.run(run())


if __name__ == "__main__":
    main()
