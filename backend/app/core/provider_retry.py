from __future__ import annotations

import random
from dataclasses import dataclass

from backend.app.core.config import get_settings


@dataclass(frozen=True, slots=True)
class ProviderRetryPolicy:
    """Immutable retry policy for external provider operations."""

    max_retries: int
    base_delay_seconds: float
    max_delay_seconds: float
    jitter_seconds: float

    def __post_init__(self) -> None:
        if self.max_retries < 0:
            raise ValueError("max_retries must be zero or greater.")

        if self.base_delay_seconds < 0:
            raise ValueError(
                "base_delay_seconds must be zero or greater."
            )

        if self.max_delay_seconds < self.base_delay_seconds:
            raise ValueError(
                "max_delay_seconds must be greater than or equal "
                "to base_delay_seconds."
            )

        if self.jitter_seconds < 0:
            raise ValueError(
                "jitter_seconds must be zero or greater."
            )

    @classmethod
    def from_settings(cls) -> "ProviderRetryPolicy":
        settings = get_settings()

        return cls(
            max_retries=settings.provider_max_retries,
            base_delay_seconds=settings.provider_retry_base_delay_seconds,
            max_delay_seconds=settings.provider_retry_max_delay_seconds,
            jitter_seconds=settings.provider_retry_jitter_seconds,
        )

    def should_retry(self, attempt: int) -> bool:
        """Return whether another attempt is permitted.

        ``attempt`` is zero-based, where zero represents the first
        provider invocation.
        """

        return attempt < self.max_retries

    def delay_for(self, attempt: int) -> float:
        """Calculate bounded exponential backoff with jitter."""

        if attempt < 0:
            raise ValueError("attempt must be zero or greater.")

        exponential_delay = min(
            self.base_delay_seconds * (2**attempt),
            self.max_delay_seconds,
        )

        jitter = (
            random.uniform(0.0, self.jitter_seconds)
            if self.jitter_seconds > 0
            else 0.0
        )

        return exponential_delay + jitter

# Backward-compatible public alias.
RetryPolicy = ProviderRetryPolicy
