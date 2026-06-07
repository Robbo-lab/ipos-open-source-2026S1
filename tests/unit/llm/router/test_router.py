# ruff: noqa: PLR6301
import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.llm.base import BaseLLMClient, LLMRequest, LLMResponse
from app.llm.core.router import ChatMessage, LLMRouteRequest, ModelRouter


class DummyClient(BaseLLMClient):
    @property
    def provider_name(self) -> str:
        return "dummy"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text=f"dummy response to: {request.prompt}")


def test_router_registration():
    router = ModelRouter()
    client = DummyClient()
    router.register_client("dummy", client)

    assert router.get_client("dummy") is client
    assert router.get_client("DUMMY") is client  # Case insensitive
    assert router.get_client("nonexistent") is None


@pytest.mark.asyncio
async def test_router_generate_success():
    router = ModelRouter()
    client = DummyClient()
    router.register_client("dummy", client)

    request = LLMRouteRequest(
        provider="dummy",
        model="test-model",
        messages=[ChatMessage(role="user", content="hello")],
    )

    response = await router.generate(request)
    assert response.text == "dummy response to: hello"


@pytest.mark.asyncio
async def test_router_generate_no_client():
    router = ModelRouter()
    request = LLMRouteRequest(
        provider="missing",
        model="test-model",
        messages=[ChatMessage(role="user", content="hello")],
    )

    with pytest.raises(ValueError, match="No client registered for provider: missing"):
        await router.generate(request)


@given(
    st.lists(st.builds(ChatMessage, role=st.text(), content=st.text()), min_size=1),
    st.text(),
    st.dictionaries(st.text(), st.text()),
)
def test_route_request_conversion(messages, model, extra):
    request = LLMRouteRequest(
        provider="test", model=model, messages=messages, extra=extra
    )

    llm_request = request.to_llm_request()

    assert llm_request.model == model
    assert llm_request.prompt == messages[-1].content
    assert len(llm_request.messages) == len(messages)
    assert llm_request.messages[0]["role"] == messages[0].role
    assert llm_request.messages[0]["content"] == messages[0].content
    assert llm_request.extra == extra
