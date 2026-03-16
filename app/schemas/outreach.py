from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class ContactChannel(str, Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"


class ResearcherInput(BaseModel):
    name: str = Field(..., description="Full name of the researcher")
    institution: str = Field(..., description="University or research institution")
    article_title: str = Field(..., description="Title of their recent article")
    article_summary: str = Field(..., description="Brief summary or topic of the article")
    research_signals: Optional[str] = Field(None, description="Additional research signals or keywords")
    channel: ContactChannel = Field(..., description="Outreach channel: email or linkedin")


class OutreachMessage(BaseModel):
    researcher_name: str
    channel: ContactChannel
    message: str
    tokens_used: int
    cost_usd: float


class BatchInput(BaseModel):
    researchers: list[ResearcherInput] = Field(
        ...,
        description="List of researchers to generate messages for",
        min_length=1,
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "researchers": [
                    {
                        "name": "Dr. Sarah Chen",
                        "institution": "Stanford University",
                        "article_title": "Metabolic Adaptation in Long-Term Caloric Restriction",
                        "article_summary": "Explores how metabolism adapts during prolonged caloric restriction and implications for longevity",
                        "research_signals": "longevity, metabolic health, caloric restriction",
                        "channel": "email"
                    }
                ]
            }
        }
    }


class BatchOutput(BaseModel):
    total: int
    successful: int
    failed: int
    messages: list[OutreachMessage]
    total_tokens: int
    total_cost_usd: float


class CostEstimate(BaseModel):
    researcher_count: int
    estimated_tokens: int
    estimated_cost_usd: float
    model: str