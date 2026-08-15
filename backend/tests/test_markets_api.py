from datetime import date, datetime, timezone

import httpx
import pytest

from backend.app.api.routes.markets import get_market_service
from backend.app.instruments import Equity, InstrumentResolver
from backend.app.main import app
from backend.app.schemas.market import HistoricalPrice, Quote
from backend.app.services.market_service import MarketService


class FakeMarketProvider:
    @property
    def name(self) -> str:
        return "fake"

    async def get_quote(self, symbol: str) -> Quote:
        return Quote(
            symbol=symbol,
            provider_symbol=symbol,
            timestamp=datetime(
                2026,
                8,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            ),
            open=750.0,
            high=760.0,
            low=745.0,
            close=755.0,
            volume=1000000,
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
    assert data["analysis"]["absolute_return"] == 7.0
    assert data["analysis"]["percentage_return"] == pytest.approx(0.9358288770053476)
    assert data["analysis"]["price_summary"]["starting_price"] == 748.0
    assert data["analysis"]["price_summary"]["latest_price"] == 755.0


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

