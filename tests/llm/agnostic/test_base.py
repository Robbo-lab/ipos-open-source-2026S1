from collections.abc import AsyncGenerator
from typing import override

import pytest

from app.llm.base import (
    BaseLLMClient,
    LLMProviderError,
    LLMRequest,
    LLMResponse,
    StreamingLLMClient,
)


def test_llm_request_dataclass():
    """Verify LLMRequest initialization and default values."""
    req = LLMRequest(prompt="test prompt")
    assert req.prompt == "test prompt"
    assert req.extra == {}


def test_llm_response_dataclass():
    """Verify LLMResponse initialization."""
    res = LLMResponse(text="test response")
    assert res.text == "test response"
    assert res.raw_response is None


def test_llm_provider_error():
    """Verify LLMProviderError can be raised and caught."""
    with pytest.raises(LLMProviderError) as excinfo:
        raise LLMProviderError("test error")
    assert str(excinfo.value) == "test error"


class DummyClient(BaseLLMClient):
    """A class that implements BaseLLMClient but not StreamingLLMClient."""

    @property
    @override
    def provider_name(self) -> str:
        return "Dummy"

    @override
    async def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text="dummy")


class DummyStreamingClient(StreamingLLMClient):
    """A class that implements both BaseLLMClient and StreamingLLMClient."""

    @property
    @override
    def provider_name(self) -> str:
        return "DummyStream"

    @override
    async def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text="dummy")

    @override
    async def stream(self, request: LLMRequest) -> AsyncGenerator[LLMResponse]:
        yield LLMResponse(text="chunk")


def test_protocol_runtime_checks():
    """Verify @runtime_checkable works for our protocols."""
    client = DummyClient()
    streaming_client = DummyStreamingClient()
    not_a_client = object()

    # BaseLLMClient checks
    assert isinstance(client, BaseLLMClient)
    assert isinstance(streaming_client, BaseLLMClient)
    assert not isinstance(not_a_client, BaseLLMClient)

    # StreamingLLMClient checks
    assert not isinstance(client, StreamingLLMClient)
    assert isinstance(streaming_client, StreamingLLMClient)
    assert not isinstance(not_a_client, StreamingLLMClient)
