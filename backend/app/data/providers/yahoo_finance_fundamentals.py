import asyncio
from datetime import datetime
from typing import Any

import yfinance as yf

from backend.app.core.exceptions import MarketDataProviderError
from backend.app.core.provider_execution import run_provider_call
from backend.app.data.providers.fundamentals import FundamentalsProvider
from backend.app.domain.fundamentals import (
    BalanceSheet,
    CashFlowStatement,
    FinancialPeriod,
    IncomeStatement,
    ValuationMetrics,
)


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
                value = value.item()
            except (ValueError, TypeError):
                pass

        if hasattr(value, "isoformat"):
            try:
                value = value.isoformat()
            except (ValueError, TypeError):
                pass

        return value

    @classmethod
    def _dataframe_to_rows(
        cls,
        dataframe: Any,
    ) -> list[dict[str, object]]:
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

    @staticmethod
    def _period(value: object) -> FinancialPeriod:
        if isinstance(value, datetime):
            period_end = value
        elif isinstance(value, str):
            period_end = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        else:
            raise ValueError(
                f"Unsupported financial period type: {type(value).__name__}"
            )

        return FinancialPeriod(period_end=period_end)

    @classmethod
    def _normalize_income_statement(
        cls,
        row: dict[str, object],
    ) -> IncomeStatement:
        return IncomeStatement(
            period=cls._period(row["period"]),
            total_revenue=row.get("Total Revenue"),
            net_income=row.get("Net Income"),
            basic_eps=row.get("Basic EPS"),
            diluted_eps=row.get("Diluted EPS"),
            net_interest_income=row.get("Net Interest Income"),
            interest_income=row.get("Interest Income"),
            interest_expense=row.get("Interest Expense"),
        )

    @classmethod
    def _normalize_balance_sheet(
        cls,
        row: dict[str, object],
    ) -> BalanceSheet:
        return BalanceSheet(
            period=cls._period(row["period"]),
            total_assets=row.get("Total Assets"),
            total_liabilities=row.get(
                "Total Liabilities Net Minority Interest"
            ),
            stockholders_equity=row.get("Stockholders Equity"),
            common_stock_equity=row.get("Common Stock Equity"),
            net_loan=row.get("Net Loan"),
            cash_and_cash_equivalents=row.get(
                "Cash And Cash Equivalents"
            ),
            tangible_book_value=row.get("Tangible Book Value"),
        )

    @classmethod
    def _normalize_cash_flow(
        cls,
        row: dict[str, object],
    ) -> CashFlowStatement:
        return CashFlowStatement(
            period=cls._period(row["period"]),
            operating_cash_flow=row.get("Operating Cash Flow"),
            free_cash_flow=row.get("Free Cash Flow"),
            capital_expenditure=row.get("Capital Expenditure"),
            cash_dividends_paid=row.get("Cash Dividends Paid"),
            changes_in_cash=row.get("Changes In Cash"),
        )

    @staticmethod
    def _normalize_valuation_metrics(
        info: dict[str, object],
    ) -> ValuationMetrics:
        return ValuationMetrics(
            market_capitalization=info.get("marketCap"),
            enterprise_value=info.get("enterpriseValue"),
            trailing_pe=info.get("trailingPE"),
            forward_pe=info.get("forwardPE"),
            price_to_book=info.get("priceToBook"),
        )

    async def get_income_statement(
        self,
        symbol: str,
    ) -> list[IncomeStatement]:
        yahoo_symbol = self._to_yahoo_symbol(symbol)

        def fetch() -> list[IncomeStatement]:
            try:
                ticker = yf.Ticker(yahoo_symbol)

                return [
                    self._normalize_income_statement(row)
                    for row in self._dataframe_to_rows(
                        ticker.income_stmt
                    )
                ]
            except ValueError:
                raise
            except Exception as exc:
                raise MarketDataProviderError(
                    "Yahoo Finance could not provide the income statement."
                ) from exc

        return await run_provider_call(
            fetch,
            operation_name="yahoo_finance.fundamentals",
        )

    async def get_balance_sheet(
        self,
        symbol: str,
    ) -> list[BalanceSheet]:
        yahoo_symbol = self._to_yahoo_symbol(symbol)

        def fetch() -> list[BalanceSheet]:
            try:
                ticker = yf.Ticker(yahoo_symbol)

                return [
                    self._normalize_balance_sheet(row)
                    for row in self._dataframe_to_rows(
                        ticker.balance_sheet
                    )
                ]
            except ValueError:
                raise
            except Exception as exc:
                raise MarketDataProviderError(
                    "Yahoo Finance could not provide the balance sheet."
                ) from exc

        return await run_provider_call(
            fetch,
            operation_name="yahoo_finance.fundamentals",
        )

    async def get_cash_flow(
        self,
        symbol: str,
    ) -> list[CashFlowStatement]:
        yahoo_symbol = self._to_yahoo_symbol(symbol)

        def fetch() -> list[CashFlowStatement]:
            try:
                ticker = yf.Ticker(yahoo_symbol)

                return [
                    self._normalize_cash_flow(row)
                    for row in self._dataframe_to_rows(
                        ticker.cashflow
                    )
                ]
            except ValueError:
                raise
            except Exception as exc:
                raise MarketDataProviderError(
                    "Yahoo Finance could not provide the cash flow statement."
                ) from exc

        return await run_provider_call(
            fetch,
            operation_name="yahoo_finance.fundamentals",
        )

    async def get_key_ratios(
        self,
        symbol: str,
    ) -> ValuationMetrics:
        yahoo_symbol = self._to_yahoo_symbol(symbol)

        def fetch() -> ValuationMetrics:
            try:
                ticker = yf.Ticker(yahoo_symbol)
                info = ticker.info

                if not isinstance(info, dict):
                    return ValuationMetrics()

                return self._normalize_valuation_metrics(info)

            except Exception as exc:
                raise MarketDataProviderError(
                    "Yahoo Finance could not provide key financial ratios."
                ) from exc

        return await run_provider_call(
            fetch,
            operation_name="yahoo_finance.fundamentals",
        )


