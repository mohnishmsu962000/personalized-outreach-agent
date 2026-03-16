import structlog
from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.schemas.outreach import (
    ResearcherInput,
    OutreachMessage,
    BatchInput,
    BatchOutput,
    CostEstimate,
)
from app.services.generator import generate_message, generate_batch
from app.services.cost import estimate_cost

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.post("/generate", response_model=OutreachMessage)
async def generate_single(researcher: ResearcherInput):
    """Generate a personalized outreach message for a single researcher."""
    try:
        return await generate_message(researcher)
    except Exception as e:
        logger.error("single_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/batch", response_model=BatchOutput)
async def generate_batch_messages(payload: BatchInput):
    """Generate personalized outreach messages for a batch of researchers."""
    if len(payload.researchers) > settings.max_batch_size:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size exceeds maximum of {settings.max_batch_size}",
        )

    results = await generate_batch(payload.researchers)

    messages = []
    failed = 0
    total_tokens = 0
    total_cost = 0.0

    for result in results:
        if isinstance(result, Exception):
            failed += 1
            logger.error("batch_item_failed", error=str(result))
        else:
            messages.append(result)
            total_tokens += result.tokens_used
            total_cost += result.cost_usd

    return BatchOutput(
        total=len(payload.researchers),
        successful=len(messages),
        failed=failed,
        messages=messages,
        total_tokens=total_tokens,
        total_cost_usd=round(total_cost, 6),
    )


@router.get("/cost-estimate", response_model=CostEstimate)
async def get_cost_estimate(researcher_count: int):
    """Estimate token usage and cost before running a batch."""
    if researcher_count < 1:
        raise HTTPException(status_code=400, detail="researcher_count must be at least 1")
    if researcher_count > 10000:
        raise HTTPException(status_code=400, detail="researcher_count too large for estimate")

    estimate = estimate_cost(researcher_count, settings.openai_model)
    return CostEstimate(**estimate)