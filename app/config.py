from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Personalized Outreach Agent"
    app_version: str = "0.1.0"
    debug: bool = False

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    max_tokens: int = 300
    temperature: float = 0.7

    # Rate limiting
    rate_limit_per_minute: int = 60

    # Batch
    max_batch_size: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()