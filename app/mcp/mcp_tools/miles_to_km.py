import math
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.exceptions import ValidationError
from app.mcp.mcp_tools.conversion import miles_to_kilometers_converter

router = APIRouter(prefix="", tags=["unit-conversion"])

MAX_TUTORIAL_MILES = 100_000
MIN_TUTORIAL_MILES = 0.0001


# --- Request/Response models for clarity ---
class MilestoKmRequest(BaseModel):
    """Request model for miles to kilometers conversion, with validation.

    Attributes: miles must be within the same supported range as the runtime
    converter.
    """

    miles: float = Field(
        ...,
        ge=MIN_TUTORIAL_MILES,
        le=MAX_TUTORIAL_MILES,
        description="Distance in miles (0.0001 to 100000)",
    )


class MilestoKmResponse(BaseModel):
    """Response model for miles to kilometers conversion.
    Attributes: result is the converted distance, operation indicates the conversion type, and audited_at is a timestamp for auditing.
    """

    result: float
    operation: str
    audited_at: float


def miles_to_kilometers_value(miles: float | None) -> float:
    """
    Convert miles to kilometers, rejecting unsupported inputs.

    Args:
        miles: Distance in miles.

    Returns:
        The distance in kilometers.

    Raises:
        ValidationError: If distance is missing, non-finite, or out of range.
    """
    if miles is None:
        raise ValidationError("Miles is required.")
    if not isinstance(miles, (int, float)):
        raise ValidationError("Miles must be a numeric value.")
    if math.isnan(miles) or math.isinf(miles):
        raise ValidationError("Miles must be a finite number.")
    if miles <= 0:
        raise ValidationError("Distance must be greater than zero.")
    if miles < MIN_TUTORIAL_MILES:
        raise ValidationError("Distance is too small to be meaningful.")
    if miles > MAX_TUTORIAL_MILES:
        raise ValidationError(
            "Distance is unrealistically large for this tutorial example."
        )

    return miles_to_kilometers_converter(miles)


@router.post("/miles-to-kilometers")
# def miles_to_kilometers(miles: float):
def miles_to_kilometers(
    body: MilestoKmRequest,
) -> MilestoKmResponse:
    """
    HTTP endpoint: convert miles to kilometers with input validation.

    Args:
        body: Request body containing the distance in miles.

    Returns:
        JSON dict with the result and operation name, or an error message.
    """
    try:
        result = miles_to_kilometers_value(body.miles)
        return MilestoKmResponse(
            result=result,
            operation="miles_to_kilometers",
            audited_at=time.time(),
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


TOOL_DEFINITION = [
    {
        "name": "miles_to_kilometers",
        "description": "Convert miles to kilometers (validates supported range)",
        "func": miles_to_kilometers_value,
        "tags": {"distance", "conversion"},
    },
]
