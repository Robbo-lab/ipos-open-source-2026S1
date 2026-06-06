from __future__ import annotations

import datetime
import uuid
from enum import StrEnum

import anyio
from pydantic import BaseModel, Field
from result import Err, Ok, Result

from app.llm.base import LLMResponse
from app.llm.core.router import LLMRouteRequest, ModelRouter


class JobStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    """Represents a background LLM generation task."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.PENDING
    request: LLMRouteRequest
    outcome: Result[LLMResponse, str] | None = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    def update_status(
        self,
        status: JobStatus,
        outcome: Result[LLMResponse, str] | None = None,
    ):
        """Helper to update status and timestamp."""
        self.status = status
        self.updated_at = datetime.datetime.now()
        if outcome is not None:
            self.outcome = outcome


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
        job = Job(request=request)
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
                if not job:
                    continue

                job.update_status(JobStatus.PROCESSING)
                try:
                    # Simple direct call to the router
                    result = await self.router.generate(job.request)
                    job.update_status(JobStatus.COMPLETED, outcome=Ok(result))
                except Exception as e:
                    job.update_status(JobStatus.FAILED, outcome=Err(str(e)))

    async def close(self):
        """Close the streams to stop the workers."""
        await self._send_stream.aclose()
        await self._receive_stream.aclose()
