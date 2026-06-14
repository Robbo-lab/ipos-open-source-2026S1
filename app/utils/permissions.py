from fastapi import HTTPException
from get_principal import Principal

READ_ROLES = {"task.read"}
READ_SCOPES = {"tasks:read"}

WRITE_ROLES = {"task.write"}
WRITE_SCOPES = {"tasks:write"}


def enforce_task_read_permissions(p: Principal) -> None:
    """Check if the principal has required roles and scopes, raising 403 if not.
    Parameters:
        p is the Principal object containing user_id, roles, and scopes.

    Raises:
        HTTPException with status 403 if required roles or scopes are missing, detailing which.
    """
    missing_roles = READ_ROLES - p.roles
    missing_scopes = READ_SCOPES - p.scopes
    if missing_roles or missing_scopes:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "missing_roles": sorted(missing_roles),
                "missing_scopes": sorted(missing_scopes),
            },
        )


def enforce_task_write_permissions(p: Principal) -> None:
    """Check if the principal has required roles and scopes, raising 403 if not.
    Parameters:
        p is the Principal object containing user_id, roles, and scopes.

    Raises:
        HTTPException with status 403 if required roles or scopes are missing, detailing which.
    """
    missing_roles = WRITE_ROLES - p.roles
    missing_scopes = WRITE_SCOPES - p.scopes
    if missing_roles or missing_scopes:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message": "This principal is not allowed to modify task data.",
                "missing_roles": sorted(missing_roles),
                "missing_scopes": sorted(missing_scopes),
            },
        )
