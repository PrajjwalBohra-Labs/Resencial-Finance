import pytest

from backend.app.analytics.returns import (
    calculate_absolute_return,
    calculate_daily_price_changes,
    calculate_market_period_summary,
    calculate_percentage_return,
    calculate_price_summary,
)
from backend.app.schemas.market import HistoricalPrice


def create_prices() -> list[HistoricalPrice]:
    return [
        HistoricalPrice(
            date="2026-08-10",
            open=100.0,
            high=110.0,
            low=95.0,
            close=100.0,
            volume=1000000,
        ),
        HistoricalPrice(
            date="2026-08-11",
            open=100.0,
            high=115.0,
            low=99.0,
            close=110.0,
            volume=1200000,
        ),
        HistoricalPrice(
            date="2026-08-12",
            open=110.0,
            high=112.0,
            low=98.0,
            close=105.0,
            volume=900000,
        ),
    ]


def test_calculate_absolute_return() -> None:
    result = calculate_absolute_return(create_prices())

    assert result == 5.0


def test_calculate_percentage_return() -> None:
    result = calculate_percentage_return(create_prices())

    assert result == pytest.approx(5.0)


def test_calculate_price_summary() -> None:
    result = calculate_price_summary(create_prices())

    assert result["starting_price"] == 100.0
    assert result["latest_price"] == 105.0
    assert result["highest_close"] == 110.0
    assert result["lowest_close"] == 100.0


def test_absolute_return_requires_two_observations() -> None:
    prices = create_prices()[:1]

    with pytest.raises(
        ValueError,
        match="At least two price observations are required",
    ):
        calculate_absolute_return(prices)


def test_percentage_return_requires_two_observations() -> None:
    prices = create_prices()[:1]

    with pytest.raises(
        ValueError,
        match="At least two price observations are required",
    ):
        calculate_percentage_return(prices)


def test_percentage_return_rejects_zero_starting_price() -> None:
    prices = create_prices()

    prices[0] = prices[0].model_copy(
        update={"close": 0.0},
    )

    with pytest.raises(
        ValueError,
        match="Starting price cannot be zero",
    ):
        calculate_percentage_return(prices)


def test_price_summary_requires_data() -> None:
    with pytest.raises(
        ValueError,
        match="At least one price observation is required",
    ):
        calculate_price_summary([])

def test_calculate_daily_price_changes() -> None:
    result = calculate_daily_price_changes(create_prices())

    assert len(result) == 3

    assert result[0].date == "2026-08-10"
    assert result[0].open_to_close_change == 0.0
    assert result[0].open_to_close_change_percentage == pytest.approx(0.0)

    assert result[1].date == "2026-08-11"
    assert result[1].open_to_close_change == 10.0
    assert result[1].open_to_close_change_percentage == pytest.approx(10.0 / 100.0 * 100.0)

    assert result[2].date == "2026-08-12"
    assert result[2].open_to_close_change == -5.0
    assert result[2].open_to_close_change_percentage == pytest.approx(-5.0 / 110.0 * 100.0)


def test_calculate_market_period_summary() -> None:
    result = calculate_market_period_summary(create_prices())

    assert result.period_high == 115.0
    assert result.period_low == 95.0
    assert result.total_volume == 3100000
    assert result.average_daily_volume == pytest.approx(1033333.3333333334)

