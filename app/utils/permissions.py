from fastapi import HTTPException
from get_principal import Principal

REQUIRED_ROLES = {"utility.read", "conversion.run"}
REQUIRED_SCOPES = {"miles:convert"}

def enforce_permissions(p: Principal):
    """Check if the principal has required roles and scopes, raising 403 if not.
    Parameters:
        p is the Principal object containing user_id, roles, and scopes.
    Raises:
        HTTPException with status 403 if required roles or scopes are missing, detailing which"""
    missing_roles  = REQUIRED_ROLES  - p.roles
    missing_scopes = REQUIRED_SCOPES - p.scopes
    if missing_roles or missing_scopes:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "missing_roles":  sorted(missing_roles),
                "missing_scopes": sorted(missing_scopes),
            },
        )