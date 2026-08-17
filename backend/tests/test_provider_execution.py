import asyncio

import pytest

from backend.app.core.exceptions import (
    DataProviderRetryableError,
    DataProviderUnavailableError,
)
from backend.app.core.provider_execution import run_provider_call
from backend.app.core.provider_retry import RetryPolicy


@pytest.mark.asyncio
async def test_provider_call_returns_result() -> None:
    result = await run_provider_call(
        lambda: "ok",
        operation_name="test.operation",
        timeout_seconds=1.0,
    )

    assert result == "ok"


@pytest.mark.asyncio
async def test_provider_call_times_out() -> None:
    def slow_operation() -> str:
        import time

        time.sleep(0.2)
        return "too late"

    with pytest.raises(DataProviderUnavailableError) as exc_info:
        await run_provider_call(
            slow_operation,
            operation_name="test.slow_operation",
            timeout_seconds=0.01,
        )

    assert "test.slow_operation" in str(exc_info.value)
    assert "timeout" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_provider_call_rejects_invalid_timeout() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        await run_provider_call(
            lambda: "ok",
            operation_name="test.operation",
            timeout_seconds=0,
        )


@pytest.mark.asyncio
async def test_provider_call_preserves_operation_exception() -> None:
    def failing_operation() -> str:
        raise RuntimeError("provider exploded")

    with pytest.raises(RuntimeError, match="provider exploded"):
        await run_provider_call(
            failing_operation,
            operation_name="test.failure",
            timeout_seconds=1.0,
        )


@pytest.mark.asyncio
async def test_provider_call_retries_transient_provider_failure() -> None:
    attempts = 0

    def operation() -> str:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise DataProviderRetryableError("temporary provider failure")

        return "recovered"

    result = await run_provider_call(
        operation,
        operation_name="test.retry",
        timeout_seconds=1.0,
        retry_policy=RetryPolicy(
            max_attempts=3,
            base_delay_seconds=0,
            jitter_ratio=0,
        ),
    )

    assert result == "recovered"
    assert attempts == 3


@pytest.mark.asyncio
async def test_provider_call_does_not_retry_unexpected_exception() -> None:
    attempts = 0

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        raise RuntimeError("unexpected failure")

    with pytest.raises(RuntimeError, match="unexpected failure"):
        await run_provider_call(
            operation,
            operation_name="test.non_retryable",
            timeout_seconds=1.0,
            retry_policy=RetryPolicy(
                max_attempts=5,
                base_delay_seconds=0,
                jitter_ratio=0,
            ),
        )

    assert attempts == 1


@pytest.mark.asyncio
async def test_provider_call_does_not_block_event_loop() -> None:
    async def heartbeat() -> str:
        await asyncio.sleep(0.01)
        return "alive"

    task = asyncio.create_task(
        run_provider_call(
            lambda: "ok",
            operation_name="test.non_blocking",
            timeout_seconds=1.0,
        )
    )

    result, heartbeat_result = await asyncio.gather(
        task,
        heartbeat(),
    )

    assert result == "ok"
    assert heartbeat_result == "alive"
from backend.app.core.exceptions import DataProviderRetryableError
from backend.app.core.provider_retry import ProviderRetryPolicy


@pytest.mark.asyncio
async def test_provider_call_retries_retryable_failure() -> None:
    attempts = 0

    def flaky_operation() -> str:
        nonlocal attempts

        attempts += 1

        if attempts < 3:
            raise DataProviderRetryableError("temporary failure")

        return "recovered"

    result = await run_provider_call(
        flaky_operation,
        operation_name="test.retry",
        timeout_seconds=1.0,
        retry_policy=ProviderRetryPolicy(
            max_retries=2,
            base_delay_seconds=0.0,
            max_delay_seconds=0.0,
            jitter_seconds=0.0,
        ),
    )

    assert result == "recovered"
    assert attempts == 3


@pytest.mark.asyncio
async def test_provider_call_does_not_retry_non_retryable_failure() -> None:
    attempts = 0

    def failing_operation() -> str:
        nonlocal attempts

        attempts += 1
        raise RuntimeError("permanent failure")

    with pytest.raises(RuntimeError, match="permanent failure"):
        await run_provider_call(
            failing_operation,
            operation_name="test.no_retry",
            timeout_seconds=1.0,
            retry_policy=ProviderRetryPolicy(
                max_retries=3,
                base_delay_seconds=0.0,
                max_delay_seconds=0.0,
                jitter_seconds=0.0,
            ),
        )

    assert attempts == 1


@pytest.mark.asyncio
async def test_provider_call_exhausts_retryable_failures() -> None:
    attempts = 0

    def failing_operation() -> str:
        nonlocal attempts

        attempts += 1
        raise DataProviderRetryableError("still unavailable")

    with pytest.raises(
        DataProviderRetryableError,
        match="still unavailable",
    ):
        await run_provider_call(
            failing_operation,
            operation_name="test.exhausted",
            timeout_seconds=1.0,
            retry_policy=ProviderRetryPolicy(
                max_retries=2,
                base_delay_seconds=0.0,
                max_delay_seconds=0.0,
                jitter_seconds=0.0,
            ),
        )

    assert attempts == 3
