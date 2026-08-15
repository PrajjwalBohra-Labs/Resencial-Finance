from datetime import date, datetime, timezone

import httpx
import pytest

from backend.app.api.routes.markets import get_market_service
from backend.app.instruments import Equity, InstrumentResolver
from backend.app.main import app
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


class FakeMarketProvider:
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
            open=750.0,
            high=760.0,
            low=745.0,
            close=755.0,
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
        assert symbol == "HDFCBANK.NS"

        return [
            HistoricalPrice(
                date="2026-08-10",
                open=740.0,
                high=750.0,
                low=735.0,
                close=748.0,
                volume=1000000,
            ),
            HistoricalPrice(
                date="2026-08-11",
                open=748.0,
                high=758.0,
                low=744.0,
                close=755.0,
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


@pytest.fixture()
def client() -> httpx.AsyncClient:
    from backend.app.instruments import InstrumentResolver

    fake_service = MarketService(
        provider=FakeMarketProvider(),
        resolver=InstrumentResolver(),
    )

    app.dependency_overrides[get_market_service] = lambda: fake_service

    transport = httpx.ASGITransport(app=app)

    return httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    )


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> None:
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_quote(client: httpx.AsyncClient) -> None:
    async with client:
        response = await client.get(
            "/api/markets/quote/HDFCBANK",
            params={"exchange": "NSE"},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "HDFCBANK"
    assert data["provider_symbol"] == "HDFCBANK.NS"
    assert data["exchange"] == "NSE"
    assert data["close"] == 755.0
    assert data["source"]["name"] == "Test Provider"
    assert data["source"]["provider"] == "fake"
    assert data["freshness"]["status"] == "fresh"


@pytest.mark.asyncio
async def test_get_history(client: httpx.AsyncClient) -> None:
    async with client:
        response = await client.get(
            "/api/markets/history/HDFCBANK",
            params={
                "exchange": "NSE",
                "start_date": "2026-08-10",
                "end_date": "2026-08-11",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "HDFCBANK"
    assert data["exchange"] == "NSE"
    assert data["count"] == 2

    assert data["data"][0]["close"] == 748.0
    assert data["data"][1]["close"] == 755.0

    analysis = data["analysis"]

    assert analysis["absolute_return"] == 7.0
    assert analysis["percentage_return"] == pytest.approx(
        0.9358288770053476,
    )
    assert analysis["cagr"] > 0
    assert analysis["maximum_drawdown"] == 0.0
    assert analysis["annualised_volatility"] == 0.0

    assert analysis["price_summary"]["starting_price"] == 748.0
    assert analysis["price_summary"]["latest_price"] == 755.0
    assert analysis["price_summary"]["highest_close"] == 755.0
    assert analysis["price_summary"]["lowest_close"] == 748.0

    assert data["source"]["name"] == "Yahoo Finance"
    assert data["source"]["provider"] == "yahoo_finance"
    assert data["freshness"]["status"] == "fresh"
    assert data["freshness"]["retrieved_at"] is not None


@pytest.mark.asyncio
async def test_get_history_rejects_invalid_dates(
    client: httpx.AsyncClient,
) -> None:
    async with client:
        response = await client.get(
            "/api/markets/history/HDFCBANK",
            params={
                "exchange": "NSE",
                "start_date": "2026-08-15",
                "end_date": "2026-08-01",
            },
        )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "start_date must be before or equal to end_date."
    )
