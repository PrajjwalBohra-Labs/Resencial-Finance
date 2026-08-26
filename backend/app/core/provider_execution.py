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
        operation_task = asyncio.create_task(
            asyncio.to_thread(operation)
        )

        try:
            result = await asyncio.wait_for(
                operation_task,
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
            if not operation_task.done():
                operation_task.cancel()

            logger.warning(
                "Provider operation timed out.",
                extra={
                    "operation_name": operation_name,
                    "attempt": attempt + 1,
                    "timeout_seconds": timeout,
                },
            )

            error = DataProviderUnavailableError(
                f"Provider operation '{operation_name}' "
                f"exceeded the configured timeout of "
                f"{timeout:g} seconds."
            )

            if not policy.should_retry(attempt):
                logger.error(
                    "Provider operation failed after timeout.",
                    extra={
                        "operation_name": operation_name,
                        "attempt": attempt + 1,
                    },
                )
                raise error from exc

            logger.info(
                "Retrying provider operation after timeout.",
                extra={
                    "operation_name": operation_name,
                    "attempt": attempt + 1,
                    "next_attempt": attempt + 2,
                    "delay_seconds": policy.delay_for(attempt),
                },
            )

            await asyncio.sleep(policy.delay_for(attempt))

        except DataProviderRetryableError:
            if not operation_task.done():
                operation_task.cancel()

            if not policy.should_retry(attempt):
                logger.error(
                    "Provider operation exhausted retries.",
                    extra={
                        "operation_name": operation_name,
                        "attempt": attempt + 1,
                    },
                )
                raise

            delay = policy.delay_for(attempt)

            logger.warning(
                "Retryable provider failure; retrying.",
                extra={
                    "operation_name": operation_name,
                    "attempt": attempt + 1,
                    "next_attempt": attempt + 2,
                    "delay_seconds": delay,
                },
            )

            await asyncio.sleep(delay)

        except BaseException:
            if not operation_task.done():
                operation_task.cancel()
            raise

    raise RuntimeError(
        f"Provider operation '{operation_name}' "
        "exhausted its retry policy unexpectedly."
    )
