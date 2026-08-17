from functools import lru_cache
from typing import Any, Literal

from pydantic import model_validator
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

    # Canonical provider resilience configuration.
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

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_provider_settings(
        cls,
        values: Any,
    ) -> Any:
        if not isinstance(values, dict):
            return values

        values = dict(values)

        if (
            "provider_max_retries" in values
            and "provider_max_attempts" not in values
        ):
            values["provider_max_attempts"] = (
                int(values["provider_max_retries"]) + 1
            )

        if (
            "provider_retry_base_delay_seconds" in values
            and "provider_retry_initial_delay_seconds" not in values
        ):
            values["provider_retry_initial_delay_seconds"] = (
                values["provider_retry_base_delay_seconds"]
            )

        if (
            "provider_retry_jitter_seconds" in values
            and "provider_retry_jitter_ratio" not in values
        ):
            base_delay = float(
                values.get(
                    "provider_retry_initial_delay_seconds",
                    0.25,
                )
            )
            jitter_seconds = float(
                values["provider_retry_jitter_seconds"]
            )

            values["provider_retry_jitter_ratio"] = (
                jitter_seconds / base_delay
                if base_delay > 0
                else 0.0
            )

        return values

    @model_validator(mode="after")
    def validate_provider_resilience(self) -> "Settings":
        if self.provider_timeout_seconds <= 0:
            raise ValueError(
                "provider_timeout_seconds must be greater than zero."
            )

        if self.provider_max_attempts < 1:
            raise ValueError(
                "provider_max_attempts must be greater than zero."
            )

        if self.provider_retry_initial_delay_seconds < 0:
            raise ValueError(
                "provider_retry_initial_delay_seconds must be zero "
                "or greater."
            )

        if self.provider_retry_max_delay_seconds < 0:
            raise ValueError(
                "provider_retry_max_delay_seconds must be zero "
                "or greater."
            )

        if (
            self.provider_retry_max_delay_seconds
            < self.provider_retry_initial_delay_seconds
        ):
            raise ValueError(
                "provider_retry_max_delay_seconds must be greater than "
                "or equal to provider_retry_initial_delay_seconds."
            )

        if self.provider_retry_jitter_ratio < 0:
            raise ValueError(
                "provider_retry_jitter_ratio must be zero or greater."
            )

        return self

    # ------------------------------------------------------------------
    # Backward-compatible Settings API.
    # ------------------------------------------------------------------

    @property
    def provider_max_retries(self) -> int:
        return self.provider_max_attempts - 1

    @property
    def provider_retry_base_delay_seconds(self) -> float:
        return self.provider_retry_initial_delay_seconds

    @property
    def provider_retry_jitter_seconds(self) -> float:
        """
        Return the historical absolute-jitter representation.

        The legacy contract uses 0.10 seconds by default. When retry
        delay is explicitly disabled, jitter is also disabled.
        """
        if self.provider_retry_initial_delay_seconds == 0:
            return 0.0

        return 0.10


@lru_cache
def get_settings() -> Settings:
    return Settings()
