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


logger = logging.getLogger(__name__)

T = TypeVar("T")


async def run_provider_call(
    operation: Callable[[], T],
    *,
    operation_name: str,
    timeout_seconds: float | None = None,
    retry_policy: ProviderRetryPolicy | RetryPolicy | None = None,
) -> T:
    """Execute a blocking provider operation with bounded retries."""

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

    logger.info(
        "provider_call_started operation=%s max_attempts=%s timeout_seconds=%s",
        operation_name,
        policy.max_attempts,
        timeout,
    )

    for attempt in range(policy.max_retries + 1):
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(operation),
                timeout=timeout,
            )

            logger.info(
                "provider_call_succeeded operation=%s attempt=%s",
                operation_name,
                attempt + 1,
            )

            return result

        except asyncio.TimeoutError as exc:
            error = DataProviderUnavailableError(
                f"Provider operation '{operation_name}' "
                f"exceeded the configured timeout of "
                f"{timeout:g} seconds."
            )

            if not policy.should_retry(attempt):
                logger.error(
                    "provider_call_failed operation=%s attempt=%s "
                    "reason=timeout",
                    operation_name,
                    attempt + 1,
                )
                raise error from exc

            delay = policy.delay_for(attempt)

            logger.warning(
                "provider_call_retry operation=%s attempt=%s "
                "reason=timeout delay_seconds=%s",
                operation_name,
                attempt + 1,
                delay,
            )

            await asyncio.sleep(delay)

        except DataProviderRetryableError:
            if not policy.should_retry(attempt):
                logger.error(
                    "provider_call_failed operation=%s attempt=%s "
                    "reason=retryable_error",
                    operation_name,
                    attempt + 1,
                )
                raise

            delay = policy.delay_for(attempt)

            logger.warning(
                "provider_call_retry operation=%s attempt=%s "
                "reason=retryable_error delay_seconds=%s",
                operation_name,
                attempt + 1,
                delay,
            )

            await asyncio.sleep(delay)

    logger.error(
        "provider_call_failed operation=%s reason=retry_policy_exhausted",
        operation_name,
    )

    raise RuntimeError(
        f"Provider operation '{operation_name}' "
        "exhausted its retry policy unexpectedly."
    )
