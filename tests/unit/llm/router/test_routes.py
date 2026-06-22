# ruff: noqa: PLR2004
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.llm.core.router import ChatMessage


@pytest.fixture
def app():
    from app.routes.route_llm import router

    app = FastAPI()
    app.include_router(router)
    return app


@pytest.mark.asyncio
async def test_route_generate_sync(app):
    with patch(
        "app.llm.state.client.models.generate_content", new_callable=AsyncMock
    ) as mock_gen:
        mock_gen.return_value = {"text": "mocked response"}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {
                "provider": "gemini",
                "model": "gemini-pro",
                "messages": [{"role": "user", "content": "hello"}],
                "extra": {"temp": 0.5},
            }
            response = await ac.post("/v1/llm/generate", json=payload)

        assert response.status_code == 200
        assert response.json() == {"text": "mocked response"}
        mock_gen.assert_called_once_with(
            provider="gemini",
            model="gemini-pro",
            contents=[ChatMessage(role="user", content="hello")],
            temp=0.5,
        )


@pytest.mark.asyncio
async def test_route_enqueue_async(app):
    with patch(
        "app.llm.state.client.models.enqueue_content", new_callable=AsyncMock
    ) as mock_enqueue:
        mock_enqueue.return_value = "job-abc"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {
                "provider": "openai",
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "async task"}],
            }
            response = await ac.post("/v1/llm/enqueue", json=payload)

        assert response.status_code == 202
        assert response.json() == {"job_id": "job-abc", "status": "pending"}


@pytest.mark.asyncio
async def test_route_get_job_status(app):
    mock_job = {
        "id": "job-123",
        "status": "completed",
        "request": {
            "provider": "test",
            "model": "test",
            "messages": [{"role": "user", "content": "hi"}],
        },
        "outcome": {"status": "ok", "root": {"text": "done"}},
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:01",
    }

    with patch(
        "app.llm.state.client.queue.get_job", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_job

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get("/v1/llm/jobs/job-123")

        assert response.status_code == 200
        assert response.json()["id"] == "job-123"
        assert response.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_route_get_job_not_found(app):
    with patch(
        "app.llm.state.client.queue.get_job", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get("/v1/llm/jobs/missing")

        assert response.status_code == 404
        assert response.json()["detail"] == "Job not found"
