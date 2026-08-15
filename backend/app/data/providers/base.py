from abc import ABC, abstractmethod


class DataProviderError(Exception):
    """Base exception for external financial-data provider failures."""


class DataProviderUnavailableError(DataProviderError):
    """Raised when a provider cannot currently be reached."""


class DataProvider(ABC):
    """Base contract for all Resencial Finance data providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        raise NotImplementedError
