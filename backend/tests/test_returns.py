import pytest

from backend.app.analytics.returns import (
    calculate_absolute_return,
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
