from abc import ABC, abstractmethod

from backend.app.core.exceptions import (
    DataProviderError,
    DataProviderRequestError,
    DataProviderResponseError,
    DataProviderUnavailableError,
)


class DataProvider(ABC):
    """Base contract for all Resencial Finance data providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        raise NotImplementedError


__all__ = [
    "DataProvider",
    "DataProviderError",
    "DataProviderRequestError",
    "DataProviderResponseError",
    "DataProviderUnavailableError",
]
