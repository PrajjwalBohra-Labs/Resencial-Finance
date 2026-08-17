class AppError(Exception):
    """Base class for application-level errors."""


class DataProviderError(AppError):
    """Base exception for external financial-data provider failures."""


class DataProviderUnavailableError(DataProviderError):
    """Raised when an external provider cannot currently be reached."""


class DataProviderRetryableError(DataProviderError):
    """Raised when a transient provider failure may be retried."""


class DataProviderRequestError(DataProviderError):
    """Raised when a provider request cannot be completed successfully."""


class DataProviderRetryableError(DataProviderRequestError):
    """Raised when a provider failure is considered safe to retry."""


class DataProviderResponseError(DataProviderError):
    """Raised when a provider returns unusable or invalid data."""


class MarketDataProviderError(DataProviderRetryableError):
    """Backward-compatible retryable market-data provider failure."""


class LLMProviderError(AppError):
    """Raised when the language-model provider cannot fulfill a request."""

