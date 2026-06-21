from unittest.mock import AsyncMock, MagicMock

import pytest

from app.llm.client import LLMClient
from app.llm.core.router import ChatMessage, LLMRouteRequest


@pytest.fixture
def mock_router():
    router = MagicMock()
    router.generate = AsyncMock()
    return router


@pytest.fixture
def mock_queue():
    queue = MagicMock()
    queue.enqueue = AsyncMock()
    return queue


@pytest.mark.asyncio
async def test_llm_client_generate_content_string(mock_router):
    client = LLMClient(router=mock_router)

    await client.models.generate_content(
        model="test-model",
        contents="hello world",
        provider="test-provider",
        temperature=0.7,
    )

    mock_router.generate.assert_called_once()
    request = mock_router.generate.call_args[0][0]
    assert isinstance(request, LLMRouteRequest)
    assert request.model == "test-model"
    assert request.provider == "test-provider"
    assert len(request.messages) == 1
    assert request.messages[0].content == "hello world"
    assert request.extra == {"temperature": 0.7}


@pytest.mark.asyncio
async def test_llm_client_generate_content_messages(mock_router):
    client = LLMClient(router=mock_router)
    messages = [
        ChatMessage(role="user", content="hi"),
        ChatMessage(role="assistant", content="hello"),
    ]

    await client.models.generate_content(model="test-model", contents=messages)

    mock_router.generate.assert_called_once()
    request = mock_router.generate.call_args[0][0]
    assert request.messages == messages


@pytest.mark.asyncio
async def test_llm_client_enqueue_content(mock_router, mock_queue):
    client = LLMClient(router=mock_router, queue=mock_queue)
    mock_queue.enqueue.return_value = "job-123"

    job_id = await client.models.enqueue_content(
        model="test-model", contents="enqueue me"
    )

    assert job_id == "job-123"
    mock_queue.enqueue.assert_called_once()
    request = mock_queue.enqueue.call_args[0][0]
    assert request.messages[0].content == "enqueue me"


@pytest.mark.asyncio
async def test_llm_client_enqueue_no_queue(mock_router):
    client = LLMClient(router=mock_router, queue=None)

    with pytest.raises(RuntimeError, match="Queue not initialized on LLMClient"):
        await client.models.enqueue_content(model="test", contents="fail")
