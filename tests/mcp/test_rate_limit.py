import asyncio
from collections.abc import Awaitable, Callable, MutableMapping
from types import SimpleNamespace
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_429_TOO_MANY_REQUESTS,
)

from app.security import rate_limit
from app.security.rate_limit import RateLimitMiddleware


# Keep the test limit small so the tests can trigger the rate limiter quickly.
TEST_RATE_LIMIT_REQUESTS = 2
TEST_RATE_LIMIT_WINDOW_SECONDS = 60


async def empty_asgi_app(
    _scope: MutableMapping[str, Any],
    _receive: Callable[[], Awaitable[MutableMapping[str, Any]]],
    _send: Callable[[MutableMapping[str, Any]], Awaitable[None]],
):
    # BaseHTTPMiddleware needs an ASGI app when it is created.
    # ASGI apps take scope, receive, and send, but this test does not use them
    # because it calls dispatch() directly instead of running a full server.
    # The empty app only exists so RateLimitMiddleware can be constructed.
    await asyncio.sleep(0)


def test_rate_limit_blocks_after_limit(monkeypatch):
    rate_limit.requests_by_ip.clear()

    # The real limit is higher, so monkeypatch lowers it for this test only.
    # Pytest restores the original values after the test finishes.
    monkeypatch.setattr(
        rate_limit,
        "RATE_LIMIT_REQUESTS",
        TEST_RATE_LIMIT_REQUESTS
    )

    monkeypatch.setattr(
        rate_limit,
        "RATE_LIMIT_WINDOW_SECONDS",
        TEST_RATE_LIMIT_WINDOW_SECONDS
    )

    # TestClient runs this small FastAPI app in the test process.
    # That means the middleware is tested without manually starting the server.
    test_app = FastAPI()
    test_app.add_middleware(RateLimitMiddleware)

    # This route gives the test a real endpoint to call.
    # If the middleware allows the request, the route returns HTTP 200.
    @test_app.get("/test")
    def test_route():
        return {"status": "ok"}

    client = TestClient(test_app)

    response_1 = client.get("/test")
    response_2 = client.get("/test")
    response_3 = client.get("/test")

    assert response_1.status_code == HTTP_200_OK
    assert response_2.status_code == HTTP_200_OK
    assert response_3.status_code == HTTP_429_TOO_MANY_REQUESTS
    assert response_3.headers["Retry-After"] == str(TEST_RATE_LIMIT_WINDOW_SECONDS)

    rate_limit.requests_by_ip.clear()


def test_rate_limit_rejects_missing_client_ip():
    async def run_test():
        middleware = RateLimitMiddleware(app=empty_asgi_app)

        # dispatch() normally receives a real Starlette Request.
        # For this focused test, only client=None matters because that is the
        # safety branch we want to check.
        request = cast(Request, cast(object, SimpleNamespace(client=None)))

        # call_next represents the next step in the middleware chain.
        # If the middleware blocks the request early, this response is not used.
        async def call_next(_request: Request):
            await asyncio.sleep(0)
            return Response("ok")

        # dispatch() is async, so this helper awaits it before making assertions.
        response = await middleware.dispatch(request, call_next)

        assert response.status_code == HTTP_400_BAD_REQUEST

    asyncio.run(run_test())


def test_rate_limit_integrates_with_api(monkeypatch):
    # Clear global state before this integration-style test starts.
    rate_limit.requests_by_ip.clear()

    # Use the same small limit values as the focused middleware test.
    monkeypatch.setattr(
        rate_limit,
        "RATE_LIMIT_REQUESTS",
        TEST_RATE_LIMIT_REQUESTS,
    )
    monkeypatch.setattr(
        rate_limit,
        "RATE_LIMIT_WINDOW_SECONDS",
        TEST_RATE_LIMIT_WINDOW_SECONDS,
    )

    # Build a small API app and attach the middleware in the same way main.py does.
    test_app = FastAPI()
    test_app.add_middleware(RateLimitMiddleware)

    # Use a health-style route so the test exercises middleware around an API endpoint.
    @test_app.get("/health")
    def health():
        return {"status": "ok"}

    client = TestClient(test_app)

    response_1 = client.get("/health")
    response_2 = client.get("/health")
    response_3 = client.get("/health")

    assert response_1.status_code == HTTP_200_OK
    assert response_2.status_code == HTTP_200_OK
    assert response_3.status_code == HTTP_429_TOO_MANY_REQUESTS
    assert response_3.headers["Retry-After"] == str(TEST_RATE_LIMIT_WINDOW_SECONDS)

    rate_limit.requests_by_ip.clear()
