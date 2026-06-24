import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from app.llm.providers.openai.models import (
    ChatCompletionAssistantMessage,
    ChatCompletionDeveloperMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionSystemMessage,
    ChatCompletionToolMessage,
    ChatCompletionUserMessage,
    ResponseFormatJsonSchema,
    Role,
    TextContentPart,
)


@given(st.text())
def test_text_content_part_property(t):
    """Property: TextContentPart should accept any string."""
    part = TextContentPart(text=t)
    assert part.text == t
    assert part.type == "text"


def test_user_message_simple():
    """Verify simple user message parsing."""
    msg = ChatCompletionUserMessage(content="Hello")
    assert msg.role == Role.USER
    assert msg.content == "Hello"


def test_system_message_simple():
    """Verify simple system message parsing."""
    msg = ChatCompletionSystemMessage(content="You are a helper")
    assert msg.role == Role.SYSTEM
    assert msg.content == "You are a helper"


def test_developer_message_simple():
    """Verify simple developer message parsing (OpenAI o1 style)."""
    msg = ChatCompletionDeveloperMessage(content="Reason carefully")
    assert msg.role == Role.DEVELOPER
    assert msg.content == "Reason carefully"


def test_assistant_message_with_refusal():
    """Verify assistant message with refusal."""
    msg = ChatCompletionAssistantMessage(content=None, refusal="I cannot do that.")
    assert msg.role == Role.ASSISTANT
    assert msg.content is None
    assert msg.refusal == "I cannot do that."


def test_tool_message():
    """Verify tool message parsing."""
    msg = ChatCompletionToolMessage(content="Success", tool_call_id="call_123")
    assert msg.role == Role.TOOL
    assert msg.content == "Success"
    assert msg.tool_call_id == "call_123"


def test_request_structured_outputs():
    """Verify that Structured Outputs configuration is correctly validated."""
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "test"}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "my_schema",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {"foo": {"type": "string"}},
                    "required": ["foo"],
                    "additionalProperties": False,
                },
            },
        },
    }
    req = ChatCompletionRequest.model_validate(payload)
    assert isinstance(req.response_format, ResponseFormatJsonSchema)
    assert req.response_format.json_schema.name == "my_schema"
    assert req.response_format.json_schema.strict is True


def test_response_parsing():
    """Verify that ChatCompletionResponse can parse a typical OpenAI response."""
    expected_total_tokens = 21
    raw_response = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Hello there!"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": expected_total_tokens,
        },
    }
    res = ChatCompletionResponse.model_validate(raw_response)
    assert res.id == "chatcmpl-123"
    assert res.choices[0].message.content == "Hello there!"
    assert res.usage is not None
    assert res.usage.total_tokens == expected_total_tokens


def test_invalid_role():
    """Verify that an invalid role raises ValidationError."""
    with pytest.raises(ValidationError):
        # Using a raw dict to trigger validation on the Annotated union
        ChatCompletionRequest.model_validate({
            "model": "gpt-4o",
            "messages": [{"role": "invalid_role", "content": "fail"}],
        })
