from __future__ import annotations

from typing import Any


def build_success_response(data: dict[str, Any], message: str = "ok") -> dict[str, Any]:
    return {"status": message, **data}


def build_error_response(
    message: str,
    code: str = "error",
    status_code: int = 400,
) -> dict[str, Any]:
    return {"status": code, "error": message, "status_code": status_code}
