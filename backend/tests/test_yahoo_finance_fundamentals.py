import pandas as pd
import pytest

from backend.app.data.providers.yahoo_finance_fundamentals import (
    YahooFinanceFundamentalsProvider,
)


class FakeTicker:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

        self.income_stmt = pd.DataFrame(
            {
                pd.Timestamp("2026-03-31"): {
                    "Total Revenue": 1000000.0,
                    "Net Income": 200000.0,
                },
                pd.Timestamp("2025-03-31"): {
                    "Total Revenue": 900000.0,
                    "Net Income": 170000.0,
                },
            }
        )

        self.balance_sheet = pd.DataFrame(
            {
                pd.Timestamp("2026-03-31"): {
                    "Total Assets": 5000000.0,
                    "Total Liabilities Net Minority Interest": 4500000.0,
                }
            }
        )

        self.cashflow = pd.DataFrame(
            {
                pd.Timestamp("2026-03-31"): {
                    "Operating Cash Flow": 250000.0,
                    "Free Cash Flow": 180000.0,
                }
            }
        )

        self.info = {
            "marketCap": 1500000000000,
            "trailingPE": 18.5,
            "forwardPE": 17.2,
            "priceToBook": 2.4,
            "returnOnEquity": 0.145,
            "debtToEquity": 520.0,
            "profitMargins": 0.18,
        }


@pytest.mark.asyncio
async def test_yahoo_fundamentals_provider_name() -> None:
    provider = YahooFinanceFundamentalsProvider()

    assert provider.name == "yahoo_finance"


@pytest.mark.asyncio
async def test_yahoo_fundamentals_provider_income_statement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.app.data.providers.yahoo_finance_fundamentals.yf.Ticker",
        FakeTicker,
    )

    provider = YahooFinanceFundamentalsProvider()

    result = await provider.get_income_statement("HDFCBANK")

    assert len(result) == 2
    assert result[0]["period"] == "2026-03-31T00:00:00"
    assert result[0]["Total Revenue"] == 1000000.0
    assert result[0]["Net Income"] == 200000.0


@pytest.mark.asyncio
async def test_yahoo_fundamentals_provider_balance_sheet(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.app.data.providers.yahoo_finance_fundamentals.yf.Ticker",
        FakeTicker,
    )

    provider = YahooFinanceFundamentalsProvider()

    result = await provider.get_balance_sheet("HDFCBANK")

    assert len(result) == 1
    assert result[0]["Total Assets"] == 5000000.0


@pytest.mark.asyncio
async def test_yahoo_fundamentals_provider_cash_flow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.app.data.providers.yahoo_finance_fundamentals.yf.Ticker",
        FakeTicker,
    )

    provider = YahooFinanceFundamentalsProvider()

    result = await provider.get_cash_flow("HDFCBANK")

    assert len(result) == 1
    assert result[0]["Operating Cash Flow"] == 250000.0


@pytest.mark.asyncio
async def test_yahoo_fundamentals_provider_key_ratios(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.app.data.providers.yahoo_finance_fundamentals.yf.Ticker",
        FakeTicker,
    )

    provider = YahooFinanceFundamentalsProvider()

    result = await provider.get_key_ratios("HDFCBANK")

    assert result["marketCap"] == 1500000000000
    assert result["trailingPE"] == 18.5
    assert result["forwardPE"] == 17.2
    assert result["priceToBook"] == 2.4
    assert result["returnOnEquity"] == 0.145
