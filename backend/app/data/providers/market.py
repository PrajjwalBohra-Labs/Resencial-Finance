from abc import abstractmethod
from datetime import date

from backend.app.data.providers.base import DataProvider
from backend.app.instruments import Equity
from backend.app.schemas.market import HistoricalPrice, Quote


class MarketDataProvider(DataProvider):
    """Interface for market-data providers."""

    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote:
        """Return the latest available quote."""
        raise NotImplementedError

    @abstractmethod
    async def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        """Return historical market prices."""
        raise NotImplementedError

    @abstractmethod
    async def get_equity(
        self,
        symbol: str,
    ) -> Equity | None:
        """Return normalized equity metadata when available."""
        raise NotImplementedError
