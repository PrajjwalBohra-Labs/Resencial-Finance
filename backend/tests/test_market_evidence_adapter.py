from datetime import date

import pytest

from backend.app.data.evidence.market_evidence_adapter import (
    MarketEvidenceAdapter,
)
from backend.app.domain.research import ResearchFocus, ResearchRequest


class FakeMarketService:
    provider_name = "fake-market-provider"

    async def get_historical_prices(
        self,
        symbol: str,
        exchange: str,
        start_date: date,
        end_date: date,
    ) -> list[dict]:
        assert symbol == "HDFCBANK"
        assert exchange == "NSE"
        assert start_date == date(2026, 8, 10)
        assert end_date == date(2026, 8, 11)

        return [
            {
                "date": date(2026, 8, 10),
                "open": 748.0,
                "high": 752.0,
                "low": 747.0,
                "close": 750.0,
                "volume": 1000000,
            },
            {
                "date": date(2026, 8, 11),
                "open": 750.0,
                "high": 757.0,
                "low": 749.0,
                "close": 755.0,
                "volume": 1200000,
            },
        ]


@pytest.mark.asyncio
async def test_market_evidence_adapter_collects_history() -> None:
    adapter = MarketEvidenceAdapter(FakeMarketService())

    request = ResearchRequest(
        question="Analyse HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        focus=ResearchFocus.MARKET,
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    result = await adapter.collect(request)

    assert len(result) == 2
    assert result[0].source_type == "market_data"
    assert result[0].source_name == "fake-market-provider"
    assert result[0].title == "HDFCBANK market price"
    assert "Close: 750.0" in result[0].content
    assert "Volume: 1000000" in result[0].content
    assert result[1].content.startswith("Date: 2026-08-11")


@pytest.mark.asyncio
async def test_market_evidence_adapter_returns_empty_without_symbols() -> None:
    adapter = MarketEvidenceAdapter(FakeMarketService())

    request = ResearchRequest(
        question="Analyse the market.",
        exchange="NSE",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    result = await adapter.collect(request)

    assert result == []


@pytest.mark.asyncio
async def test_market_evidence_adapter_returns_empty_without_exchange() -> None:
    adapter = MarketEvidenceAdapter(FakeMarketService())

    request = ResearchRequest(
        question="Analyse HDFC Bank.",
        symbols=["HDFCBANK"],
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    result = await adapter.collect(request)

    assert result == []


@pytest.mark.asyncio
async def test_market_evidence_adapter_returns_empty_without_dates() -> None:
    adapter = MarketEvidenceAdapter(FakeMarketService())

    request = ResearchRequest(
        question="Analyse HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
    )

    result = await adapter.collect(request)

    assert result == []
