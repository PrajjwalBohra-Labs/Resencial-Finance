from backend.app.core.exceptions import (
    DataProviderError,
    DataProviderRequestError,
    DataProviderResponseError,
    DataProviderRetryableError,
    DataProviderUnavailableError,
    MarketDataProviderError,
)


def test_provider_error_hierarchy() -> None:
    assert issubclass(DataProviderUnavailableError, DataProviderError)
    assert issubclass(DataProviderRequestError, DataProviderError)
    assert issubclass(
        DataProviderRetryableError,
        DataProviderRequestError,
    )
    assert issubclass(DataProviderResponseError, DataProviderError)
    assert issubclass(
        MarketDataProviderError,
        DataProviderRetryableError,
    )


def test_market_data_error_remains_a_provider_error() -> None:
    error = MarketDataProviderError("provider failed")

    assert isinstance(error, DataProviderError)
    assert isinstance(error, DataProviderRequestError)
    assert isinstance(error, DataProviderRetryableError)


def test_provider_errors_are_distinguishable() -> None:
    assert (
        DataProviderUnavailableError
        is not DataProviderRequestError
    )
    assert (
        DataProviderRequestError
        is not DataProviderResponseError
    )
