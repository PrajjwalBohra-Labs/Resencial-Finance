from __future__ import annotations

import random
from dataclasses import dataclass

from backend.app.core.config import get_settings


@dataclass(frozen=True, slots=True)
class ProviderRetryPolicy:
    """Immutable retry policy expressed as retries after the first attempt."""

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

    @property
    def max_attempts(self) -> int:
        """Return the total number of permitted provider invocations."""

        return self.max_retries + 1

    def should_retry(self, attempt: int) -> bool:
        """Return whether another attempt is permitted.

        ``attempt`` is zero-based and identifies the failed attempt.
        """

        if attempt < 0:
            raise ValueError("attempt must be zero or greater.")

        return attempt < self.max_retries

    def delay_for(self, attempt: int) -> float:
        """Calculate bounded exponential backoff with additive jitter."""

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


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Execution-facing retry policy expressed as total attempts.

    This policy is intentionally separate from ``ProviderRetryPolicy`` so
    callers can express retry behavior in the more intuitive
    ``max_attempts`` form without changing the settings-backed policy.
    """

    max_attempts: int
    base_delay_seconds: float
    jitter_ratio: float = 0.0
    max_delay_seconds: float | None = None

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be greater than zero.")

        if self.base_delay_seconds < 0:
            raise ValueError(
                "base_delay_seconds must be zero or greater."
            )

        if self.jitter_ratio < 0:
            raise ValueError(
                "jitter_ratio must be zero or greater."
            )

        if self.max_delay_seconds is not None:
            if self.max_delay_seconds < 0:
                raise ValueError(
                    "max_delay_seconds must be zero or greater."
                )

            if self.max_delay_seconds < self.base_delay_seconds:
                raise ValueError(
                    "max_delay_seconds must be greater than or equal "
                    "to base_delay_seconds."
                )

    @property
    def max_retries(self) -> int:
        """Return retries after the initial provider invocation."""

        return self.max_attempts - 1

    def should_retry(self, attempt: int) -> bool:
        """Return whether another invocation is permitted."""

        if attempt < 0:
            raise ValueError("attempt must be zero or greater.")

        return attempt < self.max_retries

    def delay_for(self, attempt: int) -> float:
        """Calculate exponential backoff with proportional jitter."""

        if attempt < 0:
            raise ValueError("attempt must be zero or greater.")

        delay = self.base_delay_seconds * (2**attempt)

        if self.max_delay_seconds is not None:
            delay = min(delay, self.max_delay_seconds)

        if self.jitter_ratio > 0 and delay > 0:
            delay += random.uniform(
                0.0,
                delay * self.jitter_ratio,
            )

        return delay
