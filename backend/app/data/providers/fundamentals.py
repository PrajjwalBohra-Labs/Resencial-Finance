from abc import abstractmethod

from backend.app.data.providers.base import DataProvider
from backend.app.domain.fundamentals import (
    BalanceSheet,
    CashFlowStatement,
    IncomeStatement,
    ValuationMetrics,
)


class FundamentalsProvider(DataProvider):
    """Interface for normalized company fundamental data."""

    @abstractmethod
    async def get_income_statement(
        self,
        symbol: str,
    ) -> list[IncomeStatement]:
        """Return normalized income-statement observations."""
        raise NotImplementedError

    @abstractmethod
    async def get_balance_sheet(
        self,
        symbol: str,
    ) -> list[BalanceSheet]:
        """Return normalized balance-sheet observations."""
        raise NotImplementedError

    @abstractmethod
    async def get_cash_flow(
        self,
        symbol: str,
    ) -> list[CashFlowStatement]:
        """Return normalized cash-flow observations."""
        raise NotImplementedError

    @abstractmethod
    async def get_key_ratios(
        self,
        symbol: str,
    ) -> ValuationMetrics:
        """Return normalized valuation metrics."""
        raise NotImplementedError
