from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import httpx
from httpx_sse import aconnect_sse

from app.llm.base import BaseLLMClient, LLMProviderError, LLMRequest, LLMResponse
from app.llm.providers.gemini.models import (
    Content,
    GenerateContentRequest,
    GenerateContentResponse,
    Role,
    TextPart,
    is_text_part,
)


class GeminiClient(BaseLLMClient):
    """An asynchronous client for the Gemini API, implementing the BaseLLMClient interface."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    ):
        """
        Initialize the GeminiClient.

        Args:
            api_key: Your Google AI Studio API key.
            model_name: The Gemini model to use.
            base_url: The base REST API URL.
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    @property
    def provider_name(self) -> str:
        """The human-readable name of the provider."""
        return "Google Gemini"

    def _build_url(self, method: str) -> str:
        """Construct the REST URL for a specific model method."""
        # Note: We append the API key here, but avoid logging the full URL in case of error
        return f"{self.base_url}/models/{self.model_name}:{method}?key={self.api_key}"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Implementation of the BaseLLMClient interface.
        Translates a generic LLMRequest into a Gemini-specific request.
        """
        # Convert generic prompt to Gemini Content
        gemini_request = GenerateContentRequest(
            contents=[Content(role=Role.USER, parts=[TextPart(text=request.prompt)])]
        )

        try:
            response = await self.generate_content(gemini_request)

            # Extract text from the first candidate
            if not response.candidates:
                return LLMResponse(text="", raw_response=response)

            first_part = response.candidates[0].content.parts[0]
            text = first_part.text if is_text_part(first_part) else ""

            return LLMResponse(text=text, raw_response=response)

        except httpx.HTTPError as e:
            # Mask the API key in the error message if it's part of the URL
            error_msg = str(e).replace(self.api_key, "REDACTED")
            raise LLMProviderError(f"Gemini API request failed: {error_msg}") from e
        except Exception as e:
            raise LLMProviderError(f"An unexpected error occurred: {e}") from e

    async def stream(self, request: LLMRequest) -> AsyncGenerator[LLMResponse]:
        """
        Implementation of the StreamingLLMClient interface.
        Translates a generic LLMRequest into a Gemini-specific streaming request.
        """
        gemini_request = GenerateContentRequest(
            contents=[Content(role=Role.USER, parts=[TextPart(text=request.prompt)])]
        )

        try:
            async for chunk in self.stream_generate_content(gemini_request):
                if not chunk.candidates:
                    continue

                first_part = chunk.candidates[0].content.parts[0]
                text = first_part.text if is_text_part(first_part) else ""

                yield LLMResponse(text=text, raw_response=chunk)

        except httpx.HTTPError as e:
            error_msg = str(e).replace(self.api_key, "REDACTED")
            raise LLMProviderError(f"Gemini API streaming failed: {error_msg}") from e
        except Exception as e:
            raise LLMProviderError(
                f"An unexpected error occurred during stream: {e}"
            ) from e

    async def generate_content(
        self,
        request: GenerateContentRequest,
        client: httpx.AsyncClient | None = None,
    ) -> GenerateContentResponse:
        """Gemini-specific method for single content generation."""
        url = self._build_url("generateContent")
        payload = request.model_dump(by_alias=True, exclude_none=True)

        if client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return GenerateContentResponse.model_validate(response.json())

        async with httpx.AsyncClient(timeout=30.0) as c:
            response = await c.post(url, json=payload)
            response.raise_for_status()
            return GenerateContentResponse.model_validate(response.json())

    async def stream_generate_content(
        self,
        request: GenerateContentRequest,
        client: httpx.AsyncClient | None = None,
    ) -> AsyncGenerator[GenerateContentResponse]:
        """Gemini-specific method for streaming content generation."""
        url = self._build_url("streamGenerateContent") + "&alt=sse"
        payload = request.model_dump(by_alias=True, exclude_none=True)

        managed_client = client is None
        c = client or httpx.AsyncClient(timeout=60.0)

        try:
            async with aconnect_sse(c, "POST", url, json=payload) as event_source:
                async for event in event_source.aiter_sse():
                    if not event.data:
                        continue
                    chunk_data = json.loads(event.data)
                    yield GenerateContentResponse.model_validate(chunk_data)
        finally:
            if managed_client:
                await c.aclose()
