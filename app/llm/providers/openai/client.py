from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import httpx
from httpx_sse import aconnect_sse
from pydantic import TypeAdapter

from app.llm.base import (
    BaseLLMClient,
    LLMProviderError,
    LLMRequest,
    LLMResponse,
    StreamingLLMClient,
)
from app.llm.providers.openai.models import (
    ChatCompletionRequest,
    ChatCompletionRequestMessage,
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    ChatCompletionUserMessage,
)


class OpenAIClient(StreamingLLMClient, BaseLLMClient):
    """
    An asynchronous client for OpenAI-compatible APIs (including OpenRouter).
    Implements the BaseLLMClient and StreamingLLMClient interfaces.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4o",
        base_url: str = "https://api.openai.com/v1",
        extra_headers: dict[str, str] | None = None,
    ):
        """
        Initialize the OpenAIClient.

        Args:
            api_key: Your OpenAI or OpenRouter API key.
            model_name: The model to use.
            base_url: The base API URL. Defaults to OpenAI.
            extra_headers: Optional headers (e.g., HTTP-Referer, X-Title for OpenRouter).
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.extra_headers = extra_headers or {}

    @property
    def provider_name(self) -> str:
        """The human-readable name of the provider."""
        if "openrouter.ai" in self.base_url:
            return "OpenRouter"
        return "OpenAI"

    def _get_headers(self) -> dict[str, str]:
        """Construct headers for the API request."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        headers.update(self.extra_headers)
        return headers

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Implementation of the BaseLLMClient interface.
        Translates a generic LLMRequest into an OpenAI-specific request.
        """
        model = request.model or self.model_name

        # If full message history is provided, use it. Otherwise fall back to single prompt.
        messages: list[ChatCompletionRequestMessage]
        if request.messages:
            messages = TypeAdapter(list[ChatCompletionRequestMessage]).validate_python(
                request.messages
            )
        else:
            messages = [ChatCompletionUserMessage(content=request.prompt)]

        openai_request = ChatCompletionRequest(
            model=model,
            messages=messages,
            stream=False,
            **request.extra,
        )

        url = f"{self.base_url}/chat/completions"
        headers = self._get_headers()
        payload = openai_request.model_dump(exclude_none=True)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = ChatCompletionResponse.model_validate(response.json())

                # Extract text from the first choice
                text = ""
                if data.choices:
                    text = data.choices[0].message.content or ""

                return LLMResponse(text=text, raw_response=data)

        except httpx.HTTPError as e:
            error_msg = str(e).replace(self.api_key, "REDACTED")
            raise LLMProviderError(
                f"{self.provider_name} API request failed: {error_msg}"
            ) from e
        except Exception as e:
            raise LLMProviderError(f"An unexpected error occurred: {e}") from e

    async def stream(self, request: LLMRequest) -> AsyncGenerator[LLMResponse]:
        """
        Implementation of the StreamingLLMClient interface.
        Translates a generic LLMRequest into an OpenAI-specific streaming request.
        """
        model = request.model or self.model_name

        messages: list[ChatCompletionRequestMessage]
        if request.messages:
            messages = TypeAdapter(list[ChatCompletionRequestMessage]).validate_python(
                request.messages
            )
        else:
            messages = [ChatCompletionUserMessage(content=request.prompt)]

        openai_request = ChatCompletionRequest(
            model=model,
            messages=messages,
            stream=True,
            **request.extra,
        )

        url = f"{self.base_url}/chat/completions"
        headers = self._get_headers()
        payload = openai_request.model_dump(exclude_none=True)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with aconnect_sse(
                    client, "POST", url, json=payload, headers=headers
                ) as event_source:
                    async for event in event_source.aiter_sse():
                        if not event.data or event.data == "[DONE]":
                            continue

                        chunk_data = json.loads(event.data)
                        chunk = ChatCompletionStreamResponse.model_validate(chunk_data)

                        if chunk.choices:
                            delta = chunk.choices[0].delta
                            text = delta.content or ""
                            yield LLMResponse(text=text, raw_response=chunk)

        except httpx.HTTPError as e:
            error_msg = str(e).replace(self.api_key, "REDACTED")
            raise LLMProviderError(
                f"{self.provider_name} API streaming failed: {error_msg}"
            ) from e
        except Exception as e:
            raise LLMProviderError(
                f"An unexpected error occurred during stream: {e}"
            ) from e
