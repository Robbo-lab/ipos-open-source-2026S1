from unittest import result
import pytest
from app.core.exceptions import ValidationException
from app.mcp.mcp_tools.miles_to_km import miles_to_kilometers_value

def test_validation_exception_is_exception():
    assert issubclass(ValidationException, Exception)

def test_negative_miles_raises_validation_exception():
    with pytest.raises(ValidationException):
        miles_to_kilometers_value(-1)

def test_zero_miles_raises_validation_exception():
    with pytest.raises(ValidationException):
        miles_to_kilometers_value(0)

def test_non_miles_raises_validation_exception():
    with pytest.raises(ValidationException):
        miles_to_kilometers_value(None)

def test_too_large_miles_raises_validation_exception():
    with pytest.raises(ValidationException):
        miles_to_kilometers_value(99999999)

def test_valid_miles_returns_float():
    result = miles_to_kilometers_value(1)
    assert round(result, 3) == 1.609

def test_http_exception_not_raises():
    from fastapi import HTTPException
    with pytest.raises(ValidationException):
        try: 
            miles_to_kilometers_value(-1)
        except HTTPException:
            pytest.fail("HTTPException should not be raised from core logic")
