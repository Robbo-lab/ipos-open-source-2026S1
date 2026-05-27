from hypothesis import given
from hypothesis import strategies as st

from app.llm.providers.gemini.models import (
    Content,
    FunctionCall,
    FunctionCallPart,
    GenerateContentRequest,
    GenerateContentResponse,
    Role,
    TextPart,
    is_function_call_part,
    is_text_part,
)


@given(st.text())
def test_text_part_property(t):
    """Property: TextPart should accept any string."""
    part = TextPart(text=t)
    assert part.text == t


def test_text_part_parsing():
    """Verify that TextPart is correctly identified and narrowed."""
    data = TextPart(text="Hello Gemini")
    content = Content(role=Role.USER, parts=[data])
    part = content.parts[0]

    assert isinstance(part, TextPart)
    assert part.text == "Hello Gemini"
    assert is_text_part(part) is True


def test_function_call_part_parsing():
    """Verify that FunctionCallPart is correctly identified and narrowed."""
    data = FunctionCallPart(
        functionCall=FunctionCall(name="get_weather", args={"location": "London"})
    )
    content = Content(role=Role.MODEL, parts=[data])
    part = content.parts[0]

    assert isinstance(part, FunctionCallPart)
    assert part.function_call.name == "get_weather"
    assert part.function_call.args == {"location": "London"}
    assert is_function_call_part(part) is True


def test_request_model_dump():
    """Verify that request model dumps to camelCase for the API."""
    req = GenerateContentRequest(
        contents=[Content(role=Role.USER, parts=[TextPart(text="test")])]
    )
    dump = req.model_dump(by_alias=True, exclude_none=True)
    assert "contents" in dump
    assert dump["contents"][0]["role"] == "user"


def test_response_parsing():
    """Verify that GenerateContentResponse can parse a typical API response."""
    expected_total_tokens = 30
    raw_response = {
        "candidates": [
            {
                "content": {"role": "model", "parts": [{"text": "Parsed response"}]},
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 10,
            "candidatesTokenCount": 20,
            "totalTokenCount": expected_total_tokens,
        },
    }
    response = GenerateContentResponse.model_validate(raw_response)
    assert len(response.candidates) == 1

    first_part = response.candidates[0].content.parts[0]
    assert is_text_part(first_part)
    assert first_part.text == "Parsed response"

    assert response.usage_metadata is not None
    assert response.usage_metadata.total_token_count == expected_total_tokens
