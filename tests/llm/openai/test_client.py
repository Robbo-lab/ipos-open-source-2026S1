import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.llm.base import LLMRequest
from app.llm.providers.openai.client import OpenAIClient


@pytest.mark.asyncio
async def test_openai_generate_success():
    """Verify the generate method with a mocked OpenAI response."""
    mock_response_data = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "OpenAI Response"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
    }

    mock_resp = Mock()
    mock_resp.json.return_value = mock_response_data
    mock_resp.status_code = 200
    mock_resp.raise_for_status = Mock()

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        client = OpenAIClient(api_key="sk-test")
        request = LLMRequest(prompt="Hello")

        response = await client.generate(request)

        assert response.text == "OpenAI Response"
        assert client.provider_name == "OpenAI"


def test_openrouter_provider_name():
    """Verify that OpenRouter is correctly identified by base_url."""
    client = OpenAIClient(api_key="sk-test", base_url="https://openrouter.ai/api/v1")
    assert client.provider_name == "OpenRouter"


def test_openrouter_extra_headers():
    """Verify that extra headers (Referer, Title) are included in the request."""
    extra_headers = {"HTTP-Referer": "https://myapp.com", "X-Title": "MyApp"}
    client = OpenAIClient(
        api_key="sk-test",
        base_url="https://openrouter.ai/api/v1",
        extra_headers=extra_headers,
    )

    headers = client._get_headers()
    assert headers["HTTP-Referer"] == "https://myapp.com"
    assert headers["X-Title"] == "MyApp"
    assert headers["Authorization"] == "Bearer sk-test"


@pytest.mark.asyncio
async def test_openai_stream_success():
    """Verify streaming content generation with mocked SSE stream."""
    chunks = [
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1677652288,
            "model": "gpt-4o",
            "choices": [
                {"index": 0, "delta": {"content": "Chunk 1"}, "finish_reason": None}
            ],
        },
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1677652288,
            "model": "gpt-4o",
            "choices": [
                {"index": 0, "delta": {"content": "Chunk 2"}, "finish_reason": "stop"}
            ],
        },
    ]

    class MockSSEEvent:
        def __init__(self, data, is_json=True):
            self.data = json.dumps(data) if is_json else data

    async def mock_aiter_sse():
        for chunk in chunks:
            await asyncio.sleep(0)
            yield MockSSEEvent(chunk)
        yield MockSSEEvent("[DONE]", is_json=False)  # OpenAI specific end marker

    mock_event_source = AsyncMock()
    mock_event_source.aiter_sse = mock_aiter_sse

    with patch("app.llm.providers.openai.client.aconnect_sse") as mock_aconnect:
        mock_aconnect.return_value.__aenter__.return_value = mock_event_source

        client = OpenAIClient(api_key="sk-test")
        request = LLMRequest(prompt="Stream me")

        results = []
        async for response in client.stream(request):
            results.append(response.text)

        assert results == ["Chunk 1", "Chunk 2"]


@pytest.mark.asyncio
async def test_openai_generate_error_handling():
    """Verify that HTTP errors are correctly caught and wrapped."""
    import httpx

    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Error", request=Mock(), response=Mock(status_code=401)
    )

    with patch(
        "httpx.AsyncClient.post", side_effect=httpx.HTTPError("Error with sk-bad-key")
    ):
        client = OpenAIClient(api_key="sk-bad-key")
        request = LLMRequest(prompt="Hello")

        from app.llm.base import LLMProviderError

        with pytest.raises(LLMProviderError) as exc:
            await client.generate(request)

        assert "REDACTED" in str(exc.value)
        assert "sk-bad-key" not in str(exc.value)
