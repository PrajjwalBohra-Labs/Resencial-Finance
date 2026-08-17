from backend.app.data.providers.fundamentals import FundamentalsProvider
from backend.app.domain.fundamentals import (
    BalanceSheet,
    CashFlowStatement,
    IncomeStatement,
    ValuationMetrics,
)


class FundamentalsService:
    """Application service for normalized company fundamental data."""

    def __init__(self, provider: FundamentalsProvider) -> None:
        self._provider = provider

    @property
    def provider_name(self) -> str:
        return self._provider.name

    async def get_income_statement(
        self,
        symbol: str,
    ) -> list[IncomeStatement]:
        return await self._provider.get_income_statement(symbol)

    async def get_balance_sheet(
        self,
        symbol: str,
    ) -> list[BalanceSheet]:
        return await self._provider.get_balance_sheet(symbol)

    async def get_cash_flow(
        self,
        symbol: str,
    ) -> list[CashFlowStatement]:
        return await self._provider.get_cash_flow(symbol)

    async def get_key_ratios(
        self,
        symbol: str,
    ) -> ValuationMetrics:
        return await self._provider.get_key_ratios(symbol)
