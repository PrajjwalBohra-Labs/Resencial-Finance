from abc import abstractmethod

from backend.app.data.providers.base import DataProvider


class FundamentalsProvider(DataProvider):
    """Interface for company fundamental-data providers."""

    @abstractmethod
    async def get_income_statement(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        """Return normalized income-statement data."""
        raise NotImplementedError

    @abstractmethod
    async def get_balance_sheet(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        """Return normalized balance-sheet data."""
        raise NotImplementedError

    @abstractmethod
    async def get_cash_flow(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        """Return normalized cash-flow data."""
        raise NotImplementedError

    @abstractmethod
    async def get_key_ratios(
        self,
        symbol: str,
    ) -> dict[str, object]:
        """Return normalized key financial ratios."""
        raise NotImplementedError
