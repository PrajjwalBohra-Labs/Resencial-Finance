from backend.app.schemas.market import HistoricalPrice
from backend.app.services.market_analysis_service import (
    MarketAnalysisService,
)


def test_market_analysis_service_analyse_prices() -> None:
    prices = [
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

    result = MarketAnalysisService.analyse_prices(prices)

    assert result.absolute_return == 5.0
    assert result.percentage_return == 5.0
    assert result.price_summary.starting_price == 100.0
    assert result.price_summary.latest_price == 105.0
