from __future__ import annotations

import asyncio
import os
from typing import Any, cast

from dotenv import load_dotenv

from app.llm.base import BaseLLMClient, LLMRequest
from app.llm.providers.gemini.client import GeminiClient
from app.llm.providers.gemini.models import (
    GenerateContentRequest,
    is_function_call_part,
    is_text_part,
)

load_dotenv()

# Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def get_available_tools() -> list[dict[str, Any]]:
    """Return the task manager tools available to the Gemini model.

    Defines the tool schemas, descriptions, and parameters that LLM can
    choose during interactions with the tasks. Definitions helps Gemini
    to choose correct tool and arguments for specific operation requested
    by users prompt.

    Returns:
        list[dict[str, Any]]: Collection of tool declarations supported
        by the task manager integration.
    """
    return [
        {
            "function_declarations": [
                {
                    "name": "create_task",
                    "description": (
                        "Create a new task in the task manager. "
                        "Use when the user wants to add a task."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "object",
                                "description": "Task data required to create a new task.",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "completed": {"type": "boolean"},
                                },
                                "required": ["name", "description"],
                            }
                        },
                        "required": ["task"],
                    },
                },
                {
                    "name": "delete_task",
                    "description": (
                        "Delete an existing task by its exact name. "
                        "Use only when the user clearly asks to delete or remove a task."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Exact name of the task to delete.",
                            }
                        },
                        "required": ["name"],
                    },
                },
                {
                    "name": "get_task_by_name",
                    "description": (
                        "Retrieve a task using its exact name. "
                        "Use when the user wants to view information about a specific task."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Exact name of the task to retrieve.",
                            }
                        },
                        "required": ["name"],
                    },
                },
                {
                    "name": "get_task_by_id",
                    "description": (
                        "Retrieve a task using its unique ID. "
                        "Use when the user provides a task ID."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                                "description": "Unique ID of the task to retrieve.",
                            }
                        },
                        "required": ["id"],
                    },
                },
                {
                    "name": "list_tasks",
                    "description": (
                        "List tasks filtered by status. "
                        "Use when the user wants to see pending or completed tasks."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_type": {
                                "type": "string",
                                "description": "Task status filter.",
                                "enum": ["Pending", "Completed"],
                            }
                        },
                        "required": ["task_type"],
                    },
                },
                {
                    "name": "complete_task",
                    "description": (
                        "Mark an existing task as completed. "
                        "Use when the user wants to finish, complete, or mark a task as done."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Exact name of the task to mark as completed.",
                            }
                        },
                        "required": ["name"],
                    },
                },
            ]
        }
    ]


async def perform_initial_turn(
    client: GeminiClient, query: str
) -> tuple[list[Any], Any]:
    """
    Creates the initial user message, registers the available tool
    definitions, and sends the request to Gemini. Then model
    decides whether a tool should be called or if a direct response
    should be returned.

    Args:
    client: Gemini client used to communicate with the model.
    query: User request for Gemini.

    Returns:
    tuple[list[Any], Any]: Conversation history and the model's
    response content from the first interaction.
    """
    messages: list[Any] = [{"role": "user", "parts": [{"text": query}]}]
    tools = get_available_tools()

    print("\n[Thinking...]")
    # Using the specific generate_content method for tool support
    response = await client.generate_content(
        GenerateContentRequest(contents=messages, tools=tools)  # type: ignore
    )
    return messages, response.candidates[0].content


def handle_manual_tool_call(call: Any) -> dict[str, Any]:
    """
    Shows the selected by LLM tools and arguments for a given task.
    Asks user to enter the tool execution result (for debugging purpose).
    The result is formatted as a function response message and returned
    to the conversation so Gemini can continue processing.

    Args:
        call: Tool call object containing the tool name and arguments
        generated by Gemini.

    Returns:
        dict[str, Any]: Function response message containing the tool
        execution result.
    """
    print("\n---- TOOL DEBUG ----")
    print("Tool:", call.name)
    print("Args:", call.args)
    print("--------------------")

    mcp_result = input("Enter the 'result' from the tool: ")

    return {
        "role": "model",
        "parts": [
            {
                "functionResponse": {
                    "name": call.name,
                    "response": {"result": mcp_result},
                }
            }
        ],
    }


async def run_simple_demo(client: BaseLLMClient) -> None:
    """
    Sends a basic prompt to the configured LLM client using the
    provider-agnostic interface and prints the model response.
    Used to make sure that the client is configured correctly.

    Args:
        client: LLM client implementation.
    """
    print("\n--- Provider-Agnostic Basic Call ---")
    user_query = "Hello, what LLM are you?"
    print(f"User: {user_query}")

    request = LLMRequest(prompt=user_query)
    response = await client.generate(request)

    print(f"Gemini: {response.text}")


async def run_mcp_demo(client: GeminiClient) -> None:
    """The main execution pipeline for the Gemini + MCP example.

    Takes the user request from terminal, sends it to Gemini,
    and checks whether the model request a tool call. If the
    tool is selected, the function sends it to Gemini so the model
    can produce a final result.

    Args:
        client: LLM client implementation.
    """
    print("\n--- Gemini MCP Simulation ---")
    user_query = input("User:")

    # 1. Start the conversation
    messages, model_turn = await perform_initial_turn(client, user_query)

    # 2. Process any tool requests
    for part in model_turn.parts:
        if is_function_call_part(part):
            tool_res_message = handle_manual_tool_call(part.function_call)

            messages.extend([model_turn.model_dump(by_alias=True), tool_res_message])

            # 3. Get the final explanation
            print("\n[Explaining...]")
            final_resp = await client.generate_content(
                GenerateContentRequest(
                    contents=messages, tools=cast(Any, get_available_tools())
                )
            )
            final_part = final_resp.candidates[0].content.parts[0]

            if is_text_part(final_part):
                print(f"\nGemini: {final_part.text}")
            return

    # If no tool was requested, just show the response
    if model_turn.parts and is_text_part(model_turn.parts[0]):
        print(f"\nGemini: {model_turn.parts[0].text}")


async def task_manager_main_async() -> None:
    if not API_KEY:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    # Create the client - notice we type it as the base interface where appropriate
    gemini_client = GeminiClient(api_key=API_KEY, model_name=MODEL)

    # Run the agnostic demo
    await run_simple_demo(gemini_client)

    # Run the specific MCP demo
    await run_mcp_demo(gemini_client)


if __name__ == "__main__":
    asyncio.run(task_manager_main_async())
