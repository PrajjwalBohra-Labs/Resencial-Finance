import pytest

from backend.app.analytics.risk import (
    calculate_annualised_volatility,
    calculate_cagr,
    calculate_max_drawdown,
)
from backend.app.schemas.market import HistoricalPrice


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


def test_calculate_cagr() -> None:
    result = calculate_cagr(create_prices())

    assert result == pytest.approx(40.03226817917236, rel=0.000001)


def test_calculate_max_drawdown() -> None:
    result = calculate_max_drawdown(create_prices())

    assert result == pytest.approx(
        -8.0,
        rel=0.0001,
    )


def test_calculate_annualised_volatility() -> None:
    result = calculate_annualised_volatility(create_prices())

    assert result > 0


def test_cagr_requires_two_observations() -> None:
    prices = [
        HistoricalPrice(
            date="2026-08-10",
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
            volume=1000,
        ),
    ]

    assert calculate_cagr(prices) is None

def test_drawdown_requires_data() -> None:
    with pytest.raises(
        ValueError,
        match="At least one price observation is required",
    ):
        calculate_max_drawdown([])


def test_volatility_requires_two_observations() -> None:
    prices = [
        HistoricalPrice(
            date="2026-08-10",
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
            volume=1000,
        ),
    ]

    assert calculate_annualised_volatility(prices) is None

def test_cagr_rejects_zero_price() -> None:
    prices = create_prices()

    prices[0] = prices[0].model_copy(
        update={"close": 0.0},
    )

    with pytest.raises(
        ValueError,
        match="Prices must be greater than zero",
    ):
        calculate_cagr(prices)


def test_drawdown_rejects_non_positive_peak() -> None:
    prices = create_prices()

    prices[0] = prices[0].model_copy(
        update={"close": 0.0},
    )

    with pytest.raises(
        ValueError,
        match="Prices must be greater than zero",
    ):
        calculate_max_drawdown(prices)


def test_volatility_rejects_non_positive_price() -> None:
    prices = create_prices()

    prices[0] = prices[0].model_copy(
        update={"close": 0.0},
    )

    with pytest.raises(
        ValueError,
        match="Prices must be greater than zero",
    ):
        calculate_annualised_volatility(prices)


