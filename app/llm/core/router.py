from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.llm.base import BaseLLMClient, LLMRequest, LLMResponse


class ChatMessage(BaseModel):
    """A single turn in a conversation."""

    role: str = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The text content of the message")


class LLMRouteRequest(BaseModel):
    """A unified request for routing to different LLM providers."""

    provider: str = Field(
        ..., description="The provider name (e.g., 'gemini', 'openai')"
    )
    model: str = Field(..., description="The specific model ID to use")
    messages: list[ChatMessage] = Field(..., description="The conversation history")
    extra: dict[str, Any] = Field(
        default_factory=dict, description="Provider-specific parameters"
    )

    def to_llm_request(self) -> LLMRequest:
        """Convert to the agnostic LLMRequest."""
        prompt = ""
        if self.messages:
            last_msg = self.messages[-1]
            prompt = last_msg.content

        messages = [m.model_dump() for m in self.messages]

        return LLMRequest(
            prompt=prompt,
            messages=messages,
            model=self.model,
            extra=self.extra.copy(),
        )


class ModelRouter:
    """Registry and routing logic for multiple LLM providers."""

    def __init__(self):
        self._clients: dict[str, BaseLLMClient] = {}

    def register_client(self, name: str, client: BaseLLMClient) -> None:
        """Register a new LLM client under a provider name."""
        self._clients[name.lower()] = client

    def get_client(self, name: str) -> BaseLLMClient | None:
        """Retrieve a registered client."""
        return self._clients.get(name.lower())

    async def generate(self, request: LLMRouteRequest) -> LLMResponse:
        """Route the request to the correct client and generate a response."""
        client = self.get_client(request.provider)
        if not client:
            raise ValueError(f"No client registered for provider: {request.provider}")
        return await client.generate(request.to_llm_request())
