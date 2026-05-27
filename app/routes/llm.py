from fastapi import APIRouter, HTTPException

from app.llm.core.queue import Job
from app.llm.core.router import LLMRouteRequest
from app.llm.state import client

router = APIRouter(prefix="/v1/llm", tags=["llm"])


@router.post("/generate")
async def generate_sync(request: LLMRouteRequest):
    """
    Generate content synchronously.
    Uses the LLMClient.models.generate_content pattern.
    """
    try:
        return await client.models.generate_content(
            provider=request.provider,
            model=request.model,
            contents=request.messages,
            **request.extra,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/enqueue", status_code=202)
async def generate_async(request: LLMRouteRequest):
    """
    Enqueue content for background generation.
    Uses the LLMClient.models.enqueue_content pattern.
    """
    try:
        job_id = await client.models.enqueue_content(
            provider=request.provider,
            model=request.model,
            contents=request.messages,
            **request.extra,
        )
        return {"job_id": job_id, "status": "pending"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/jobs/{job_id}", response_model=Job)
async def get_job_status(job_id: str):
    """Check the status and result of a background job."""
    if not client.queue:
        raise HTTPException(status_code=500, detail="Queue not initialized")

    job = await client.queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
