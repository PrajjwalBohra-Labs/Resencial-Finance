from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import TypeVar

from backend.app.core.config import get_settings
from backend.app.core.exceptions import (
    DataProviderRetryableError,
    DataProviderUnavailableError,
)
from backend.app.core.provider_retry import (
    ProviderRetryPolicy,
    RetryPolicy,
)


T = TypeVar("T")

logger = logging.getLogger(__name__)


async def run_provider_call(
    operation: Callable[[], T],
    *,
    operation_name: str,
    timeout_seconds: float | None = None,
    retry_policy: ProviderRetryPolicy | RetryPolicy | None = None,
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
        worker = asyncio.to_thread(operation)

        try:
            result = await asyncio.wait_for(
                worker,
                timeout=timeout,
            )

            logger.info(
                "Provider operation succeeded.",
                extra={
                    "operation_name": operation_name,
                    "attempt": attempt + 1,
                },
            )

            return result

        except asyncio.TimeoutError as exc:
            if hasattr(worker, "close"):
                worker.close()

            error = DataProviderUnavailableError(
                f"Provider operation '{operation_name}' "
                f"exceeded the configured timeout of "
                f"{timeout:g} seconds."
            )

            if not policy.should_retry(attempt):
                logger.error(
                    "Provider operation timed out.",
                    extra={
                        "operation_name": operation_name,
                        "attempt": attempt + 1,
                        "timeout_seconds": timeout,
                    },
                    exc_info=True,
                )
                raise error from exc

            logger.warning(
                "Provider operation timed out; retrying.",
                extra={
                    "operation_name": operation_name,
                    "attempt": attempt + 1,
                    "next_attempt": attempt + 2,
                    "timeout_seconds": timeout,
                },
            )

            await asyncio.sleep(policy.delay_for(attempt))

        except DataProviderRetryableError as exc:
            logger.warning(
                "Provider operation failed with retryable error; retrying."
                if policy.should_retry(attempt)
                else "Provider operation failed after retryable error.",
                extra={
                    "operation_name": operation_name,
                    "attempt": attempt + 1,
                    "next_attempt": (
                        attempt + 2
                        if policy.should_retry(attempt)
                        else None
                    ),
                    "error_type": type(exc).__name__,
                },
            )

            if not policy.should_retry(attempt):
                logger.error(
                    "Provider operation exhausted retry policy.",
                    extra={
                        "operation_name": operation_name,
                        "attempt": attempt + 1,
                    },
                    exc_info=True,
                )
                raise

            await asyncio.sleep(policy.delay_for(attempt))

    raise RuntimeError(
        f"Provider operation '{operation_name}' "
        "exhausted its retry policy unexpectedly."
    )
