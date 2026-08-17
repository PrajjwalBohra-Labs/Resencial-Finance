from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import TypeVar

from backend.app.core.config import get_settings
from backend.app.core.exceptions import (
    DataProviderRetryableError,
    DataProviderUnavailableError,
)
from backend.app.core.provider_retry import ProviderRetryPolicy


T = TypeVar("T")


async def run_provider_call(
    operation: Callable[[], T],
    *,
    operation_name: str,
    timeout_seconds: float | None = None,
    retry_policy: ProviderRetryPolicy | None = None,
) -> T:
    """Execute a blocking provider operation with bounded retries.

    Retry decisions are driven exclusively by domain-level retryable
    exceptions. All other exceptions propagate immediately.
    """

    settings = get_settings()

    timeout = (
        settings.provider_timeout_seconds
        if timeout_seconds is None
        else timeout_seconds
    )

    if timeout <= 0:
        raise ValueError("timeout_seconds must be greater than zero.")

    policy = (
        ProviderRetryPolicy.from_settings()
        if retry_policy is None
        else retry_policy
    )

    for attempt in range(policy.max_retries + 1):
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(operation),
                timeout=timeout,
            )

        except asyncio.TimeoutError as exc:
            error = DataProviderUnavailableError(
                f"Provider operation '{operation_name}' "
                f"exceeded the configured timeout of "
                f"{timeout:g} seconds."
            )

            if not policy.should_retry(attempt):
                raise error from exc

            await asyncio.sleep(policy.delay_for(attempt))

        except DataProviderRetryableError:
            if not policy.should_retry(attempt):
                raise

            await asyncio.sleep(policy.delay_for(attempt))

    raise RuntimeError(
        f"Provider operation '{operation_name}' "
        "exhausted its retry policy unexpectedly."
    )
