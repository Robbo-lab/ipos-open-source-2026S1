import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.llm.base import LLMRequest
from app.llm.providers.gemini.client import GeminiClient
from app.llm.providers.gemini.models import (
    Content,
    GenerateContentRequest,
    Role,
    TextPart,
    is_text_part,
)


@given(
    st.text(min_size=1, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")))
)
def test_build_url_property(method_name):
    """Property: _build_url should correctly include the method and API key."""
    api_key = "test-key"
    client = GeminiClient(api_key=api_key)
    url = client._build_url(method_name)
    assert f":{method_name}" in url
    assert f"key={api_key}" in url


@pytest.mark.asyncio
async def test_generate_success():
    """Verify the provider-agnostic generate method."""
    mock_response_data = {
        "candidates": [
            {"content": {"role": "model", "parts": [{"text": "Agnostic response"}]}}
        ],
        "usageMetadata": {
            "promptTokenCount": 5,
            "candidatesTokenCount": 5,
            "totalTokenCount": 10,
        },
    }

    from unittest.mock import Mock

    mock_resp = Mock()
    mock_resp.json.return_value = mock_response_data
    mock_resp.status_code = 200
    mock_resp.raise_for_status = Mock()

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        client = GeminiClient(api_key="fake-key")
        request = LLMRequest(prompt="Hello")

        response = await client.generate(request)

        assert response.text == "Agnostic response"


@pytest.mark.asyncio
async def test_generate_content_success():
    """Verify unary content generation with mocked HTTP response."""
    expected_token_count = 10
    mock_response_data = {
        "candidates": [
            {"content": {"role": "model", "parts": [{"text": "Mocked response"}]}}
        ],
        "usageMetadata": {
            "promptTokenCount": 5,
            "candidatesTokenCount": 5,
            "totalTokenCount": expected_token_count,
        },
    }

    # Mock httpx response (httpx.Response.json is sync)
    from unittest.mock import Mock

    mock_resp = Mock()
    mock_resp.json.return_value = mock_response_data
    mock_resp.status_code = 200
    mock_resp.raise_for_status = Mock()

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        client = GeminiClient(api_key="fake-key")
        request = GenerateContentRequest(
            contents=[Content(role=Role.USER, parts=[TextPart(text="Hi")])]
        )

        response = await client.generate_content(request)

        first_part = response.candidates[0].content.parts[0]
        assert is_text_part(first_part)
        assert first_part.text == "Mocked response"

        assert response.usage_metadata is not None
        assert response.usage_metadata.total_token_count == expected_token_count


@pytest.mark.asyncio
async def test_stream_generate_content_success():
    """Verify streaming content generation with mocked SSE stream."""
    # Mock data chunks (must include required 'role')
    chunks = [
        {
            "candidates": [
                {"content": {"role": "model", "parts": [{"text": "Part 1 "}]}}
            ]
        },
        {"candidates": [{"content": {"role": "model", "parts": [{"text": "Part 2"}]}}]},
    ]

    class MockSSEEvent:
        def __init__(self, data):
            self.data = json.dumps(data)

    async def mock_aiter_sse():
        for chunk in chunks:
            await asyncio.sleep(0)  # Use async feature to satisfy RUF029
            yield MockSSEEvent(chunk)

    mock_event_source = AsyncMock()
    mock_event_source.aiter_sse = mock_aiter_sse

    # We patch aconnect_sse context manager
    with patch("app.llm.providers.gemini.client.aconnect_sse") as mock_aconnect:
        mock_aconnect.return_value.__aenter__.return_value = mock_event_source

        client = GeminiClient(api_key="fake-key")
        request = GenerateContentRequest(
            contents=[Content(role=Role.USER, parts=[TextPart(text="Stream me")])]
        )

        results = []
        async for response in client.stream_generate_content(request):
            part = response.candidates[0].content.parts[0]
            if is_text_part(part):
                results.append(part.text)

        assert results == ["Part 1 ", "Part 2"]
