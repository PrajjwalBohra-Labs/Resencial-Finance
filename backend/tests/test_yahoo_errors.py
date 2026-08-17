import pytest

import yfinance.exceptions as yf_exceptions

from backend.app.core.exceptions import (
    DataProviderRequestError,
    DataProviderResponseError,
    DataProviderRetryableError,
    DataProviderUnavailableError,
    MarketDataProviderError,
)
from backend.app.core.yahoo_errors import classify_yahoo_exception


def _exception_without_constructor(
    exception_type: type[Exception],
) -> Exception:
    instance = exception_type.__new__(exception_type)
    Exception.__init__(instance)
    return instance


def test_timeout_is_unavailable() -> None:
    result = classify_yahoo_exception(
        TimeoutError("timed out"),
        operation_name="market.quote",
    )

    assert isinstance(result, DataProviderUnavailableError)


def test_connection_error_is_unavailable() -> None:
    result = classify_yahoo_exception(
        ConnectionError("connection failed"),
        operation_name="market.quote",
    )

    assert isinstance(result, DataProviderUnavailableError)


def test_rate_limit_is_retryable() -> None:
    result = classify_yahoo_exception(
        _exception_without_constructor(
            yf_exceptions.YFRateLimitError,
        ),
        operation_name="market.quote",
    )

    assert isinstance(result, DataProviderRetryableError)


def test_missing_prices_are_response_errors() -> None:
    result = classify_yahoo_exception(
        _exception_without_constructor(
            yf_exceptions.YFPricesMissingError,
        ),
        operation_name="market.historical_prices",
    )

    assert isinstance(result, DataProviderResponseError)


def test_missing_ticker_is_response_error() -> None:
    result = classify_yahoo_exception(
        _exception_without_constructor(
            yf_exceptions.YFTickerMissingError,
        ),
        operation_name="market.equity",
    )

    assert isinstance(result, DataProviderResponseError)


def test_missing_timezone_is_response_error() -> None:
    result = classify_yahoo_exception(
        _exception_without_constructor(
            yf_exceptions.YFTzMissingError,
        ),
        operation_name="market.quote",
    )

    assert isinstance(result, DataProviderResponseError)


def test_invalid_period_is_request_error() -> None:
    result = classify_yahoo_exception(
        _exception_without_constructor(
            yf_exceptions.YFInvalidPeriodError,
        ),
        operation_name="market.quote",
    )

    assert isinstance(result, DataProviderRequestError)


def test_value_error_is_response_error() -> None:
    result = classify_yahoo_exception(
        ValueError("invalid provider data"),
        operation_name="fundamentals.income_statement",
    )

    assert isinstance(result, DataProviderResponseError)


def test_unknown_exception_remains_market_provider_error() -> None:
    result = classify_yahoo_exception(
        RuntimeError("unexpected upstream failure"),
        operation_name="market.quote",
    )

    assert isinstance(result, MarketDataProviderError)


def test_existing_provider_error_is_preserved() -> None:
    original = DataProviderResponseError("already classified")

    result = classify_yahoo_exception(
        original,
        operation_name="market.quote",
    )

    assert result is original

