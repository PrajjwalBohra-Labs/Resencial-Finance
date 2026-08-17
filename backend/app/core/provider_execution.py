import asyncio
from collections.abc import Callable
from typing import TypeVar

from backend.app.core.config import get_settings
from backend.app.core.exceptions import DataProviderUnavailableError


T = TypeVar("T")


async def run_provider_call(
    operation: Callable[[], T],
    *,
    operation_name: str,
    timeout_seconds: float | None = None,
) -> T:
    """Execute a blocking provider operation under an application deadline."""

    timeout = (
        get_settings().provider_timeout_seconds
        if timeout_seconds is None
        else timeout_seconds
    )

    if timeout <= 0:
        raise ValueError("timeout_seconds must be greater than zero.")

    try:
        return await asyncio.wait_for(
            asyncio.to_thread(operation),
            timeout=timeout,
        )
    except asyncio.TimeoutError as exc:
        raise DataProviderUnavailableError(
            f"Provider operation '{operation_name}' "
            f"exceeded the configured timeout of {timeout:g} seconds."
        ) from exc
