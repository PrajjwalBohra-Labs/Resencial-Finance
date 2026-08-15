from abc import abstractmethod
from datetime import date

from backend.app.data.providers.base import DataProvider


class MacroDataProvider(DataProvider):
    """Interface for Indian macroeconomic data providers."""

    @abstractmethod
    async def get_series(
        self,
        series_name: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, object]]:
        """Return a normalized macroeconomic time series."""
        raise NotImplementedError

    @abstractmethod
    async def get_latest(
        self,
        series_name: str,
    ) -> dict[str, object] | None:
        """Return the latest available observation."""
        raise NotImplementedError
