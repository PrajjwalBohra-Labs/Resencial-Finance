from datetime import date, datetime, timezone

import pytest

from backend.app.data.providers.market import MarketDataProvider
from backend.app.instruments import Equity, InstrumentResolver
from backend.app.schemas import (
    DataFreshness,
    HistoricalPrice,
    Quote,
    Source,
)
from backend.app.services.market_service import MarketService


TEST_SOURCE = Source(
    name="Test Provider",
    type="market_data",
    provider="fake",
)


class FakeMarketProvider(MarketDataProvider):
    @property
    def name(self) -> str:
        return "fake"

    async def get_quote(self, symbol: str) -> Quote:
        observed_at = datetime(
            2026,
            8,
            15,
            10,
            0,
            tzinfo=timezone.utc,
        )

        return Quote(
            symbol=symbol,
            provider_symbol=symbol,
            timestamp=observed_at,
            open=99.0,
            high=101.0,
            low=98.0,
            close=100.0,
            volume=1000000,
            source=TEST_SOURCE,
            freshness=DataFreshness(
                observed_at=observed_at,
                retrieved_at=observed_at,
                status="fresh",
            ),
        )

    async def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        return [
            HistoricalPrice(
                date="2026-08-10",
                open=99.0,
                high=101.0,
                low=98.0,
                close=100.0,
                volume=1000000,
            ),
            HistoricalPrice(
                date="2026-08-11",
                open=100.0,
                high=106.0,
                low=99.0,
                close=105.0,
                volume=1200000,
            ),
        ]

    async def get_equity(
        self,
        symbol: str,
    ) -> Equity | None:
        return Equity(
            symbol=symbol,
            name="Test Company",
            exchange="NSE",
        )


def create_service() -> MarketService:
    return MarketService(
        provider=FakeMarketProvider(),
        resolver=InstrumentResolver(),
    )


@pytest.mark.asyncio
async def test_market_service_provider_name() -> None:
    service = create_service()

    assert service.provider_name == "fake"


@pytest.mark.asyncio
async def test_market_service_get_quote() -> None:
    service = create_service()

    result = await service.get_quote(
        symbol="HDFCBANK",
        exchange="NSE",
    )

    assert result.symbol == "HDFCBANK"
    assert result.exchange == "NSE"
    assert result.provider_symbol == "HDFCBANK.NS"
    assert result.close == 100.0
    assert result.source.name == "Test Provider"
    assert result.source.provider == "fake"
    assert result.freshness.status == "fresh"


@pytest.mark.asyncio
async def test_market_service_get_historical_prices() -> None:
    service = create_service()

    result = await service.get_historical_prices(
        symbol="HDFCBANK",
        exchange="NSE",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    assert len(result) == 2
    assert result[0].close == 100.0
    assert result[1].close == 105.0


@pytest.mark.asyncio
async def test_market_service_rejects_invalid_date_range() -> None:
    service = create_service()

    with pytest.raises(
        ValueError,
        match=r"start_date must be before or equal to end_date\.",
    ):
        await service.get_historical_prices(
            symbol="HDFCBANK",
            exchange="NSE",
            start_date=date(2026, 8, 15),
            end_date=date(2026, 8, 1),
        )


@pytest.mark.asyncio
async def test_market_service_get_equity() -> None:
    service = create_service()

    result = await service.get_equity(
        symbol="HDFCBANK",
        exchange="NSE",
    )

    assert result is not None
    assert result.symbol == "HDFCBANK"
    assert result.exchange == "NSE"
