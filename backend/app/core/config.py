from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Resencial Finance"
    app_env: Literal["development", "testing", "production"] = "development"
    app_version: str = "0.1.0"

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    frontend_url: str = "http://localhost:3000"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = ""

    provider_timeout_seconds: float = 15.0
    provider_max_retries: int = 2
    provider_retry_base_delay_seconds: float = 0.25
    provider_retry_max_delay_seconds: float = 2.0
    provider_retry_jitter_seconds: float = 0.1
    provider_max_attempts: int = 3
    provider_retry_initial_delay_seconds: float = 0.25
    provider_retry_max_delay_seconds: float = 2.0
    provider_retry_jitter_ratio: float = 0.20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


