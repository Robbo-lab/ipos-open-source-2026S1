
from fastapi import Header, HTTPException
from pydantic import BaseModel


class Principal(BaseModel):
    user_id: str
    roles: set[str] = set()
    scopes: set[str] = set()


# TODO Replace with real auth: verify token, extract roles/scopes.
def get_current_principal(
    authorisation: str | None = Header(default=None, alias="Authorization"),
) -> Principal:
    """
    For de
        accept Bearer tokens like 'Bearer demo-token-<role>'.
    Parameters:
        authorisation is the Authorization header, expected to be a Bearer token.

    Returns:
        a Principal class object with user_id, roles, and scopes.
    """
    if not authorisation or not authorisation.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorisation.split(" ", 1)[1]

    # Demo permission to principal mapping—replace with JWT claims extraction
    roles = {"utility.read", "conversion.run"} if "demo-token" in token else set()
    scopes = {"miles:convert"} if "demo-token" in token else set()
    return Principal(user_id="demo-llm-client", roles=roles, scopes=scopes)
