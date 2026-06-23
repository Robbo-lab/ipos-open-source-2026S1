"""
Shared response helper for HTTP and MCP outputs.

Provides consistent success and error response formatting
at the transport boundary, keeping business logic separate
from response shaping.
"""


def build_success_response(data: dict) -> dict:
    """
    Build a consistent success response payload.

    Args:
        data: The response data to include.

    Returns:
        A dict with ok=True and the provided data.
    """
    return {"ok": True, "data": data}


def build_error_response(message: str) -> dict:
    """
    Build a consistent error response payload.

    Args:
        message: A human-readable error message.

    Returns:
        A dict with ok=False and the error message.
    """
    return {"ok": False, "error": message}
