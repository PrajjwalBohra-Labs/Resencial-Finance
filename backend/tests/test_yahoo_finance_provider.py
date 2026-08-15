from datetime import date, datetime

import pandas as pd
import pytest
from types import SimpleNamespace
from unittest.mock import patch

from backend.app.data.providers.yahoo_finance import YahooFinanceMarketProvider


def test_nse_symbol_conversion() -> None:
    provider = YahooFinanceMarketProvider()

    assert provider._to_yahoo_symbol("HDFCBANK", "NSE") == "HDFCBANK.NS"


def test_bse_symbol_conversion() -> None:
    provider = YahooFinanceMarketProvider()

    assert provider._to_yahoo_symbol("500180", "BSE") == "500180.BO"


def test_existing_suffix_is_preserved() -> None:
    provider = YahooFinanceMarketProvider()

    assert provider._to_yahoo_symbol(
        "HDFCBANK.NS",
        "NSE",
    ) == "HDFCBANK.NS"


@pytest.mark.asyncio
async def test_get_historical_prices() -> None:
    provider = YahooFinanceMarketProvider()

    index = pd.to_datetime(
        [
            "2026-08-10",
            "2026-08-11",
        ]
    )

    history = pd.DataFrame(
        {
            "Open": [1900.0, 1910.0],
            "High": [1920.0, 1930.0],
            "Low": [1890.0, 1900.0],
            "Close": [1915.0, 1925.0],
            "Volume": [1000000, 1200000],
        },
        index=index,
    )

    fake_ticker = SimpleNamespace(
        history=lambda **kwargs: history,
    )

    with patch(
        "backend.app.data.providers.yahoo_finance.yf.Ticker",
        return_value=fake_ticker,
    ):
        result = await provider.get_historical_prices(
            "HDFCBANK.NS",
            date(2026, 8, 10),
            date(2026, 8, 12),
        )

    assert len(result) == 2
    assert result[0].close == 1915.0
    assert result[1].close == 1925.0
    assert result[1].volume == 1200000


@pytest.mark.asyncio
async def test_get_quote() -> None:
    provider = YahooFinanceMarketProvider()

    index = pd.to_datetime(
        [
            "2026-08-15 10:00:00",
        ]
    )

    history = pd.DataFrame(
        {
            "Open": [1900.0],
            "High": [1920.0],
            "Low": [1890.0],
            "Close": [1915.0],
            "Volume": [1000000],
        },
        index=index,
    )

    fake_ticker = SimpleNamespace(
        history=lambda **kwargs: history,
    )

    with patch(
        "backend.app.data.providers.yahoo_finance.yf.Ticker",
        return_value=fake_ticker,
    ):
        result = await provider.get_quote("HDFCBANK.NS")

    assert result.provider_symbol == "HDFCBANK.NS"
    assert result.close == 1915.0
    assert result.volume == 1000000
    assert isinstance(result.timestamp, datetime)
    assert result.source.name == "Yahoo Finance"
    assert result.source.provider == "yahoo_finance"
    assert result.freshness.status == "fresh"
    assert result.freshness.observed_at == result.timestamp
    assert result.freshness.retrieved_at is not None
