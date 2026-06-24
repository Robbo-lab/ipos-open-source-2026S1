from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.llm.base import LLMResponse
from app.llm.core.router import ChatMessage, LLMRouteRequest

if TYPE_CHECKING:
    from app.llm.core.queue import AnyIOModelQueue
    from app.llm.core.router import ModelRouter


class LLMClient:
    """
    A unified high-level client for all LLM providers.
    Provides a clean, SDK-like interface.
    """

    def __init__(self, router: ModelRouter, queue: AnyIOModelQueue | None = None):
        self.router = router
        self.queue = queue
        self.models = ModelNamespace(router, queue)


class ModelNamespace:
    """Namespace for model-related operations."""

    def __init__(self, router: ModelRouter, queue: AnyIOModelQueue | None = None):
        self.router = router
        self.queue = queue

    async def generate_content(
        self,
        model: str,
        contents: str | list[ChatMessage],
        provider: str = "gemini",
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Unified method to generate content synchronously (awaitable).

        Args:
            model: The model ID to use.
            contents: Either a simple string prompt or a list of ChatMessage objects.
            provider: The provider to route to (default: 'gemini').
            **kwargs: Additional provider-specific parameters.
        """
        # Normalize contents to a list of ChatMessages
        if isinstance(contents, str):
            messages = [ChatMessage(role="user", content=contents)]
        else:
            messages = contents

        # Build the routing request
        request = LLMRouteRequest(
            provider=provider, model=model, messages=messages, extra=kwargs
        )

        # Delegate to the router
        return await self.router.generate(request)

    async def enqueue_content(
        self,
        model: str,
        contents: str | list[ChatMessage],
        provider: str = "gemini",
        **kwargs: Any,
    ) -> str:
        """
        Unified method to enqueue content for background generation.

        Args:
            model: The model ID to use.
            contents: Either a simple string prompt or a list of ChatMessage objects.
            provider: The provider to route to (default: 'gemini').
            **kwargs: Additional provider-specific parameters.

        Returns:
            The unique job_id for the background task.
        """
        if not self.queue:
            raise RuntimeError("Queue not initialized on LLMClient")

        # Normalize contents to a list of ChatMessages
        if isinstance(contents, str):
            messages = [ChatMessage(role="user", content=contents)]
        else:
            messages = contents

        # Build the routing request
        request = LLMRouteRequest(
            provider=provider, model=model, messages=messages, extra=kwargs
        )

        # Delegate to the queue
        return await self.queue.enqueue(request)
