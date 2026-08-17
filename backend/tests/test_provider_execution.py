import asyncio

import pytest

from backend.app.core.exceptions import (
    DataProviderUnavailableError,
)
from backend.app.core.provider_execution import run_provider_call


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
