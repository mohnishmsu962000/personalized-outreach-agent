import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pathlib import Path

from app.config import get_settings
from app.schemas.outreach import ResearcherInput, OutreachMessage, ContactChannel
from app.services.cost import calculate_cost

logger = structlog.get_logger()

settings = get_settings()

client = AsyncOpenAI(api_key=settings.openai_api_key)

template_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent / "prompts"),
    autoescape=select_autoescape(disabled_extensions=("j2",)),
)


def _render_prompt(researcher: ResearcherInput) -> str:
    template_name = (
        "email.j2"
        if researcher.channel == ContactChannel.EMAIL
        else "linkedin.j2"
    )
    template = template_env.get_template(template_name)
    return template.render(
        name=researcher.name,
        institution=researcher.institution,
        article_title=researcher.article_title,
        article_summary=researcher.article_summary,
        research_signals=researcher.research_signals,
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
async def _call_llm(prompt: str) -> tuple[str, int, int]:
    response = await client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
        messages=[
            {
                "role": "system",
                "content": "You are an expert science communicator writing outreach messages for a health intelligence platform.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    message = response.choices[0].message.content.strip()
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    return message, input_tokens, output_tokens


async def generate_message(researcher: ResearcherInput) -> OutreachMessage:
    log = logger.bind(researcher=researcher.name, channel=researcher.channel)

    try:
        prompt = _render_prompt(researcher)
        log.info("generating_message")

        message, input_tokens, output_tokens = await _call_llm(prompt)
        cost = calculate_cost(input_tokens, output_tokens, settings.openai_model)

        log.info(
            "message_generated",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=round(cost, 6),
        )

        return OutreachMessage(
            researcher_name=researcher.name,
            channel=researcher.channel,
            message=message,
            tokens_used=input_tokens + output_tokens,
            cost_usd=round(cost, 6),
        )

    except Exception as e:
        log.error("generation_failed", error=str(e))
        raise


async def generate_batch(researchers: list[ResearcherInput]) -> list[OutreachMessage | Exception]:
    import asyncio
    tasks = [generate_message(r) for r in researchers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results