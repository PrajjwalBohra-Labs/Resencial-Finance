from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.core.exceptions import (
    DataProviderUnavailableError,
)
from backend.app.core.provider_execution import run_provider_call
from backend.app.core.provider_retry import RetryPolicy


@pytest.mark.asyncio
async def test_provider_execution_logs_success() -> None:
    operation = MagicMock(return_value="ok")

    with patch(
        "backend.app.core.provider_execution.logger"
    ) as logger:
        result = await run_provider_call(
            operation,
            operation_name="news.http.search",
            timeout_seconds=1.0,
            retry_policy=RetryPolicy(
                max_attempts=1,
                base_delay_seconds=0,
            ),
        )

    assert result == "ok"
    logger.info.assert_called()


@pytest.mark.asyncio
async def test_provider_execution_logs_retry() -> None:
    operation = MagicMock(
        side_effect=[
            DataProviderUnavailableError("temporary failure"),
            "ok",
        ]
    )

    with patch(
        "backend.app.core.provider_execution.logger"
    ) as logger, patch(
        "backend.app.core.provider_execution.asyncio.sleep",
        new=AsyncMock(),
    ):
        result = await run_provider_call(
            operation,
            operation_name="news.http.search",
            timeout_seconds=1.0,
            retry_policy=RetryPolicy(
                max_attempts=2,
                base_delay_seconds=0,
            ),
        )

    assert result == "ok"
    logger.warning.assert_called()


@pytest.mark.asyncio
async def test_provider_execution_logs_timeout_failure() -> None:
    async def slow_operation():
        raise AssertionError("operation should execute in worker thread")

    with patch(
        "backend.app.core.provider_execution.asyncio.wait_for",
        side_effect=__import__("asyncio").TimeoutError,
    ), patch(
        "backend.app.core.provider_execution.logger"
    ) as logger:
        with pytest.raises(DataProviderUnavailableError):
            await run_provider_call(
                lambda: "never",
                operation_name="news.http.search",
                timeout_seconds=1.0,
                retry_policy=RetryPolicy(
                    max_attempts=1,
                    base_delay_seconds=0,
                ),
            )

    logger.error.assert_called()
