from __future__ import annotations

import datetime
import uuid
from enum import StrEnum
from typing import Literal

import anyio
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from app.llm.base import LLMResponse
from app.llm.core.router import LLMRouteRequest, ModelRouter


class JobStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BaseJob(BaseModel):
    """Common fields for all Job states."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request: LLMRouteRequest
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class PendingJob(BaseJob):
    """A job that is waiting in the queue."""

    status: Literal[JobStatus.PENDING] = JobStatus.PENDING


class ProcessingJob(BaseJob):
    """A job that is currently being executed by a worker."""

    status: Literal[JobStatus.PROCESSING] = JobStatus.PROCESSING


class FinishedJob(BaseJob):
    """A job that has reached a terminal state (Success or Failure)."""

    status: Literal[JobStatus.COMPLETED, JobStatus.FAILED]
    outcome: Result[LLMResponse, str]


type Job = PendingJob | ProcessingJob | FinishedJob


class AnyIOModelQueue:
    """A background task queue for LLM requests using AnyIO streams."""

    def __init__(
        self,
        router: ModelRouter,
        max_workers: int = 5,
        buffer_size: int = 100,
    ):
        self.router = router
        self.max_workers = max_workers
        self._jobs: dict[str, Job] = {}

        # Initialize streams
        self._send_stream, self._receive_stream = anyio.create_memory_object_stream(
            buffer_size
        )

    async def enqueue(self, request: LLMRouteRequest) -> str:
        """
        Create a job, add it to the store, and push it to the queue.
        Returns the job_id.
        """
        job = PendingJob(request=request)
        self._jobs[job.id] = job
        await self._send_stream.send(job.id)
        return job.id

    async def get_job(self, job_id: str) -> Job | None:
        """Retrieve a job by its ID from the store."""
        return self._jobs.get(job_id)

    async def run_worker_pool(self) -> None:
        """
        The entry point for the background task group.
        Spawns and manages the worker tasks.
        """
        async with anyio.create_task_group() as tg:
            for i in range(self.max_workers):
                tg.start_soon(self._worker, i)

    async def _worker(self, worker_id: int) -> None:
        """
        Individual worker logic that pulls from the stream
        and calls the router directly.
        """
        async with self._receive_stream.clone() as receiver:
            async for job_id in receiver:
                job = self._jobs.get(job_id)
                if not job or job.status != JobStatus.PENDING:
                    continue

                # Transition to processing
                now = datetime.datetime.now()
                processing_job = ProcessingJob(
                    **job.model_dump(exclude={"status", "updated_at"}),
                    updated_at=now,
                )
                self._jobs[job_id] = processing_job

                try:
                    # Simple direct call to the router
                    result = await self.router.generate(job.request)
                    # Transition to completed
                    self._jobs[job_id] = FinishedJob(
                        **processing_job.model_dump(exclude={"status", "updated_at"}),
                        status=JobStatus.COMPLETED,
                        outcome=Ok[LLMResponse](root=result),
                        updated_at=datetime.datetime.now(),
                    )
                except Exception as e:
                    # Transition to failed
                    self._jobs[job_id] = FinishedJob(
                        **processing_job.model_dump(exclude={"status", "updated_at"}),
                        status=JobStatus.FAILED,
                        outcome=Err[str](root=str(e)),
                        updated_at=datetime.datetime.now(),
                    )

    async def wait_for_result(
        self, job_id: str, poll_interval: float = 0.1, timeout: float = 10
    ) -> LLMResponse:
        """Wait for a job to complete and return the result.

        Polls the job store until the job reaches a terminal state.
        Raises ValueError if the job fails or times out.
        """
        deadline = anyio.current_time() + timeout
        while True:
            job = self._jobs.get(job_id)
            if isinstance(job, FinishedJob):
                outcome = job.outcome

                if outcome.status == "ok":
                    if not isinstance(outcome.root, LLMResponse):
                        raise TypeError(
                            f"Expected LLMResponse, got {type(outcome.root).__name__}"
                        )
                    return outcome.root

                raise ValueError(f"Job failed: {outcome.root}")
            if anyio.current_time() > deadline:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")
            await anyio.sleep(poll_interval)

    async def close(self):
        """Close the streams to stop the workers."""
        await self._send_stream.aclose()
        await self._receive_stream.aclose()


@dataclass
class Ok[T]:
    """Successful result container."""

    root: T
    status: Literal["ok"] = "ok"


@dataclass
class Err[E]:
    """Error result container."""

    root: E
    status: Literal["error"] = "error"


type Result[T, E] = Ok[T] | Err[E]
