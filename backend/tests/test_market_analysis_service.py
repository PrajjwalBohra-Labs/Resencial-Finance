import pytest

from backend.app.schemas.market import HistoricalPrice
from backend.app.services.market_analysis_service import (
    MarketAnalysisService,
)


def create_prices() -> list[HistoricalPrice]:
    return [
        HistoricalPrice(
            date="2025-08-10",
            open=100.0,
            high=105.0,
            low=99.0,
            close=100.0,
            volume=1000000,
        ),
        HistoricalPrice(
            date="2025-10-10",
            open=110.0,
            high=112.0,
            low=108.0,
            close=110.0,
            volume=1000000,
        ),
        HistoricalPrice(
            date="2025-12-10",
            open=125.0,
            high=128.0,
            low=120.0,
            close=125.0,
            volume=1000000,
        ),
        HistoricalPrice(
            date="2026-02-10",
            open=118.0,
            high=120.0,
            low=110.0,
            close=115.0,
            volume=1000000,
        ),
        HistoricalPrice(
            date="2026-08-10",
            open=140.0,
            high=145.0,
            low=138.0,
            close=140.0,
            volume=1000000,
        ),
    ]


def test_market_analysis_service_analyse_prices() -> None:
    result = MarketAnalysisService.analyse_prices(create_prices())

    assert result.absolute_return == 40.0
    assert result.percentage_return == 40.0
    assert result.cagr == pytest.approx(
        40.03226817917236,
        rel=0.000001,
    )
    assert result.maximum_drawdown == pytest.approx(
        -8.0,
        rel=0.0001,
    )
    assert result.annualised_volatility > 0

    assert result.price_summary.starting_price == 100.0
    assert result.price_summary.latest_price == 140.0
    assert result.price_summary.highest_close == 140.0
    assert result.price_summary.lowest_close == 100.0
