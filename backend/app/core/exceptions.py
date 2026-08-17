class AppError(Exception):
    """Base class for application-level errors."""


class DataProviderError(AppError):
    """Base exception for external financial-data provider failures."""


class DataProviderUnavailableError(DataProviderError):
    """Raised when an external provider cannot currently be reached."""


class DataProviderRequestError(DataProviderError):
    """Raised when a provider request cannot be completed successfully."""


class DataProviderResponseError(DataProviderError):
    """Raised when a provider returns unusable or invalid data."""


class MarketDataProviderError(DataProviderRequestError):
    """Backward-compatible market-data provider failure."""
    

class LLMProviderError(AppError):
    """Raised when the language-model provider cannot fulfill a request."""
