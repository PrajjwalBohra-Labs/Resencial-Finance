import asyncio
from typing import Any

import yfinance as yf

from backend.app.core.exceptions import MarketDataProviderError
from backend.app.data.providers.fundamentals import FundamentalsProvider


class YahooFinanceFundamentalsProvider(FundamentalsProvider):
    """Fundamental-data provider backed by Yahoo Finance."""

    @property
    def name(self) -> str:
        return "yahoo_finance"

    @staticmethod
    def _to_yahoo_symbol(symbol: str) -> str:
        normalized = symbol.strip().upper()

        if "." in normalized:
            return normalized

        return f"{normalized}.NS"

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if hasattr(value, "item"):
            try:
                return value.item()
            except (ValueError, TypeError):
                pass

        if hasattr(value, "isoformat"):
            try:
                return value.isoformat()
            except (ValueError, TypeError):
                pass

        return value

    @classmethod
    def _dataframe_to_rows(cls, dataframe: Any) -> list[dict[str, object]]:
        if dataframe is None or getattr(dataframe, "empty", True):
            return []

        rows: list[dict[str, object]] = []

        for period in dataframe.columns:
            row: dict[str, object] = {
                "period": cls._normalize_value(period),
            }

            for field in dataframe.index:
                value = dataframe.loc[field, period]

                if value is None:
                    continue

                try:
                    if value != value:
                        continue
                except (TypeError, ValueError):
                    pass

                row[str(field)] = cls._normalize_value(value)

            rows.append(row)

        return rows

    async def get_income_statement(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        yahoo_symbol = self._to_yahoo_symbol(symbol)

        def fetch() -> list[dict[str, object]]:
            try:
                ticker = yf.Ticker(yahoo_symbol)
                return self._dataframe_to_rows(ticker.income_stmt)
            except Exception as exc:
                raise MarketDataProviderError(
                    "Yahoo Finance could not provide the income statement."
                ) from exc

        return await asyncio.to_thread(fetch)

    async def get_balance_sheet(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        yahoo_symbol = self._to_yahoo_symbol(symbol)

        def fetch() -> list[dict[str, object]]:
            try:
                ticker = yf.Ticker(yahoo_symbol)
                return self._dataframe_to_rows(ticker.balance_sheet)
            except Exception as exc:
                raise MarketDataProviderError(
                    "Yahoo Finance could not provide the balance sheet."
                ) from exc

        return await asyncio.to_thread(fetch)

    async def get_cash_flow(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        yahoo_symbol = self._to_yahoo_symbol(symbol)

        def fetch() -> list[dict[str, object]]:
            try:
                ticker = yf.Ticker(yahoo_symbol)
                return self._dataframe_to_rows(ticker.cashflow)
            except Exception as exc:
                raise MarketDataProviderError(
                    "Yahoo Finance could not provide the cash flow statement."
                ) from exc

        return await asyncio.to_thread(fetch)

    async def get_key_ratios(
        self,
        symbol: str,
    ) -> dict[str, object]:
        yahoo_symbol = self._to_yahoo_symbol(symbol)

        def fetch() -> dict[str, object]:
            try:
                ticker = yf.Ticker(yahoo_symbol)
                info = ticker.info

                if not isinstance(info, dict):
                    return {}

                fields = [
                    "marketCap",
                    "enterpriseValue",
                    "trailingPE",
                    "forwardPE",
                    "priceToBook",
                    "returnOnEquity",
                    "returnOnAssets",
                    "debtToEquity",
                    "profitMargins",
                    "operatingMargins",
                    "grossMargins",
                    "revenueGrowth",
                    "earningsGrowth",
                    "dividendYield",
                ]

                result: dict[str, object] = {}

                for field in fields:
                    value = info.get(field)

                    if value is None:
                        continue

                    result[field] = self._normalize_value(value)

                return result

            except Exception as exc:
                raise MarketDataProviderError(
                    "Yahoo Finance could not provide key financial ratios."
                ) from exc

        return await asyncio.to_thread(fetch)
