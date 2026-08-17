from __future__ import annotations

import asyncio

import socket
from typing import NoReturn

import yfinance.exceptions as yf_exceptions

from backend.app.core.exceptions import (
    DataProviderError,
    DataProviderRequestError,
    DataProviderResponseError,
    DataProviderRetryableError,
    DataProviderUnavailableError,
    MarketDataProviderError,
)


def classify_yahoo_exception(
    exc: Exception,
    *,
    operation_name: str,
) -> DataProviderError:
    """Translate known Yahoo/upstream failures into domain-level errors.

    Unknown exceptions deliberately remain request errors only when they
    represent an external provider failure. Programming errors should not
    be silently converted here.
    """

    if isinstance(exc, DataProviderError):
        return exc

    if isinstance(
        exc,
        (
            TimeoutError,
            asyncio.TimeoutError,
            ConnectionError,
            socket.timeout,
            socket.gaierror,
        ),
    ):
        return DataProviderUnavailableError(
            f"Yahoo Finance operation '{operation_name}' "
            "is temporarily unavailable."
        )

    if isinstance(exc, yf_exceptions.YFRateLimitError):
        return DataProviderRetryableError(
            f"Yahoo Finance rate-limited operation '{operation_name}'."
        )

    if isinstance(
        exc,
        (
            yf_exceptions.YFTzMissingError,
            yf_exceptions.YFTickerMissingError,
        ),
    ):
        return DataProviderResponseError(
            f"Yahoo Finance returned unusable instrument data for "
            f"operation '{operation_name}'."
        )

    if isinstance(exc, yf_exceptions.YFPricesMissingError):
        return DataProviderResponseError(
            f"Yahoo Finance returned no usable price data for "
            f"operation '{operation_name}'."
        )

    if isinstance(exc, yf_exceptions.YFInvalidPeriodError):
        return DataProviderRequestError(
            f"Yahoo Finance rejected the requested period for "
            f"operation '{operation_name}'."
        )

    if isinstance(exc, ValueError):
        return DataProviderResponseError(
            f"Yahoo Finance returned invalid data for "
            f"operation '{operation_name}'."
        )

    return MarketDataProviderError(
        f"Yahoo Finance could not complete operation '{operation_name}'."
    )


def raise_classified_yahoo_exception(
    exc: Exception,
    *,
    operation_name: str,
) -> NoReturn:
    """Raise the appropriate domain exception while preserving the cause."""

    classified = classify_yahoo_exception(
        exc,
        operation_name=operation_name,
    )

    if classified is exc:
        raise exc

    raise classified from exc


