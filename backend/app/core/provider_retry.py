from __future__ import annotations

import random
from dataclasses import dataclass

from backend.app.core.config import get_settings


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Immutable execution policy for bounded provider retries."""

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

    @classmethod
    def from_settings(cls) -> "RetryPolicy":
        settings = get_settings()

        return cls(
            max_attempts=settings.provider_max_attempts,
            base_delay_seconds=settings.provider_retry_initial_delay_seconds,
            max_delay_seconds=settings.provider_retry_max_delay_seconds,
            jitter_ratio=settings.provider_retry_jitter_ratio,
        )

    @property
    def max_retries(self) -> int:
        """Number of retries permitted after the initial attempt."""

        return self.max_attempts - 1

    def should_retry(self, attempt: int) -> bool:
        """Return whether another attempt is permitted.

        ``attempt`` is zero-based and identifies the failed attempt.
        """

        if attempt < 0:
            raise ValueError("attempt must be zero or greater.")

        return attempt < self.max_retries

    def delay_for(self, attempt: int) -> float:
        """Return bounded exponential backoff with proportional jitter."""

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


@dataclass(frozen=True, slots=True)
class ProviderRetryPolicy:
    """Compatibility policy using retry-count semantics.

    New application code should use ``RetryPolicy``. This adapter preserves
    the existing provider retry contract while deriving its defaults from
    the canonical application settings.
    """

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
        policy = RetryPolicy.from_settings()

        return cls(
            max_retries=policy.max_retries,
            base_delay_seconds=policy.base_delay_seconds,
            max_delay_seconds=(
                policy.max_delay_seconds
                if policy.max_delay_seconds is not None
                else policy.base_delay_seconds
            ),
            jitter_seconds=0.0,
        )

    @property
    def max_attempts(self) -> int:
        return self.max_retries + 1

    def should_retry(self, attempt: int) -> bool:
        if attempt < 0:
            raise ValueError("attempt must be zero or greater.")

        return attempt < self.max_retries

    def delay_for(self, attempt: int) -> float:
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
