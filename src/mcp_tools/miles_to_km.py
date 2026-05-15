from fastapi import HTTPException, APIRouter
from pydantic import BaseModel, Field
import math, time

router = APIRouter(prefix="", tags=["unit-conversion"])

# --- Request/Response models for clarity ---
class MilestoKmRequest(BaseModel):
    """Request model for miles to kilometers conversion, with validation.
    Attributes: ge=0 ensures non-negative input, and description provides API documentation."""
    miles: float = Field(..., ge=0, description="Distance in miles (>= 0)")

class MilestoKmResponse(BaseModel):
    """Response model for miles to kilometers conversion.
    Attributes: result is the converted distance, operation indicates the conversion type, and audited_at is a timestamp for auditing."""
    result: float
    operation: str
    audited_at: float

def miles_to_kilometers_value(miles: float) -> float:
    """
    Convert miles to kilometers, rejecting negative inputs.

    Args:
        miles: Distance in miles.

    Returns:
        The distance in kilometers.

    Raises:
        ValueError: If a negative distance is provided.
    """

    MAX_TUTORIAL_MILES = 100_000

    if miles is None:
        raise HTTPException(status_code=422, detail="Miles is required.")
    elif not isinstance(miles, (int, float)):
        raise HTTPException(status_code=422, detail="Miles must be a numeric value.")
    elif math.isnan(miles) or math.isinf(miles):
        raise HTTPException(status_code=422, detail="Miles must be a finite number.")
    elif miles <= 0:
        raise HTTPException(status_code=422, detail="Distance must be greater than zero.")
    elif miles < 0.0001:
        raise HTTPException(
            status_code=422,
            detail="Distance is too small to be meaningful."
        )
    elif miles > MAX_TUTORIAL_MILES:
        raise HTTPException(
            status_code=422,
            detail="Distance is unrealistically large for this tutorial example."
        )

    return miles / 0.621371

@router.post("/miles-to-kilometers")
# def miles_to_kilometers(miles: float):
def miles_to_kilometers(
        body: MilestoKmRequest,
        ) -> MilestoKmResponse:
    """
    HTTP endpoint: convert miles to kilometers with input validation.

    Args:
        miles: Distance in miles.

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
    except ValueError as exc:  # Keep HTTP response friendly
        raise HTTPException(status_code=400, detail=str(exc))

TOOL_DEFINITION = [
    {
        "name": "miles_to_kilometers",
        "description": "Convert miles to kilometers (validates non‑negative input)",
        "func": miles_to_kilometers_value,
        "tags": {"distance", "conversion"},
    },
]
