from typing import override

import anyio
import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.llm.base import LLMResponse
from app.llm.core.queue import (
    AnyIOModelQueue,
    Err,
    FinishedJob,
    JobStatus,
    Ok,
)
from app.llm.core.router import ChatMessage, LLMRouteRequest, ModelRouter


class DummyRouter(ModelRouter):
    def __init__(self, should_fail=False):
        super().__init__()
        self.should_fail = should_fail
        self.call_count = 0

    @override
    async def generate(self, request: LLMRouteRequest) -> LLMResponse:
        self.call_count += 1
        if self.should_fail:
            raise ValueError("Injected failure")
        return LLMResponse(text=f"Processed: {request.messages[0].content}")


@pytest.mark.asyncio
async def test_queue_enqueue_and_get():
    router = DummyRouter()
    queue = AnyIOModelQueue(router)

    request = LLMRouteRequest(
        provider="dummy",
        model="test",
        messages=[ChatMessage(role="user", content="task 1")],
    )

    job_id = await queue.enqueue(request)
    job = await queue.get_job(job_id)

    assert job is not None
    assert job.id == job_id
    assert job.status == JobStatus.PENDING
    assert job.request.messages[0].content == "task 1"


@pytest.mark.asyncio
async def test_queue_worker_success():
    router = DummyRouter()
    queue = AnyIOModelQueue(router, max_workers=1)

    request = LLMRouteRequest(
        provider="dummy",
        model="test",
        messages=[ChatMessage(role="user", content="task success")],
    )

    job_id = await queue.enqueue(request)

    # Run workers in a task group and cancel it after processing
    async with anyio.create_task_group() as tg:
        tg.start_soon(queue.run_worker_pool)

        # Wait for job to complete
        job = None
        for _ in range(20):
            job = await queue.get_job(job_id)
            if isinstance(job, FinishedJob) and job.status == JobStatus.COMPLETED:
                break
            await anyio.sleep(0.1)

        assert isinstance(job, FinishedJob)
        assert job.status == JobStatus.COMPLETED
        assert isinstance(job.outcome, Ok)
        res = job.outcome.root
        assert isinstance(res, LLMResponse)
        assert res.text == "Processed: task success"

        tg.cancel_scope.cancel()


@pytest.mark.asyncio
async def test_queue_worker_failure():
    router = DummyRouter(should_fail=True)
    queue = AnyIOModelQueue(router, max_workers=1)

    request = LLMRouteRequest(
        provider="dummy",
        model="test",
        messages=[ChatMessage(role="user", content="task fail")],
    )

    job_id = await queue.enqueue(request)

    async with anyio.create_task_group() as tg:
        tg.start_soon(queue.run_worker_pool)

        job = None
        for _ in range(20):
            job = await queue.get_job(job_id)
            if isinstance(job, FinishedJob) and job.status == JobStatus.FAILED:
                break
            await anyio.sleep(0.1)

        assert isinstance(job, FinishedJob)
        assert job.status == JobStatus.FAILED
        assert isinstance(job.outcome, Err)
        err_msg = job.outcome.root
        assert isinstance(err_msg, str)
        assert "Injected failure" in err_msg

        tg.cancel_scope.cancel()


@pytest.mark.asyncio
async def test_queue_wait_for_result_success():
    router = DummyRouter()
    queue = AnyIOModelQueue(router, max_workers=1)

    request = LLMRouteRequest(
        provider="dummy",
        model="test",
        messages=[ChatMessage(role="user", content="wait success")],
    )

    job_id = await queue.enqueue(request)

    async with anyio.create_task_group() as tg:
        tg.start_soon(queue.run_worker_pool)

        response = await queue.wait_for_result(job_id)
        assert response.text == "Processed: wait success"

        tg.cancel_scope.cancel()


@pytest.mark.asyncio
async def test_queue_wait_for_result_failure():
    router = DummyRouter(should_fail=True)
    queue = AnyIOModelQueue(router, max_workers=1)

    request = LLMRouteRequest(
        provider="dummy",
        model="test",
        messages=[ChatMessage(role="user", content="wait failure")],
    )

    job_id = await queue.enqueue(request)

    async with anyio.create_task_group() as tg:
        tg.start_soon(queue.run_worker_pool)

        with pytest.raises(ValueError, match="Job failed: Injected failure"):
            await queue.wait_for_result(job_id)

        tg.cancel_scope.cancel()


@given(st.lists(st.text(min_size=1), min_size=2, max_size=5, unique=True))
@pytest.mark.asyncio
async def test_job_id_uniqueness_prop(contents):
    router = DummyRouter()
    queue = AnyIOModelQueue(router)
    job_ids = set()

    for content in contents:
        request = LLMRouteRequest(
            provider="dummy",
            model="test",
            messages=[ChatMessage(role="user", content=content)],
        )
        job_id = await queue.enqueue(request)
        job_ids.add(job_id)

    assert len(job_ids) == len(contents)
