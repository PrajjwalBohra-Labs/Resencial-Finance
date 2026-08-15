import math
from datetime import date

from backend.app.schemas.market import HistoricalPrice


def calculate_cagr(
    prices: list[HistoricalPrice],
) -> float:
    """Calculate CAGR as a percentage."""
    if len(prices) < 2:
        raise ValueError(
            "At least two price observations are required."
        )

    starting_price = prices[0].close
    ending_price = prices[-1].close

    if starting_price <= 0 or ending_price <= 0:
        raise ValueError(
            "Prices must be greater than zero."
        )

    start_date = date.fromisoformat(prices[0].date)
    end_date = date.fromisoformat(prices[-1].date)

    days = (end_date - start_date).days

    if days <= 0:
        raise ValueError(
            "Price observations must span a positive time period."
        )

    years = days / 365.25

    if years <= 0:
        raise ValueError(
            "The analysis period must be greater than zero."
        )

    return (
        ((ending_price / starting_price) ** (1 / years)) - 1
    ) * 100


def calculate_max_drawdown(
    prices: list[HistoricalPrice],
) -> float:
    """Calculate maximum peak-to-trough drawdown as a percentage."""
    if not prices:
        raise ValueError(
            "At least one price observation is required."
        )

    peak = prices[0].close
    maximum_drawdown = 0.0

    for price in prices:
        if price.close > peak:
            peak = price.close

        if peak <= 0:
            raise ValueError(
                "Prices must be greater than zero."
            )

        drawdown = ((price.close - peak) / peak) * 100

        if drawdown < maximum_drawdown:
            maximum_drawdown = drawdown

    return maximum_drawdown


def calculate_annualised_volatility(
    prices: list[HistoricalPrice],
) -> float:
    """Calculate annualised historical volatility as a percentage."""
    if len(prices) < 2:
        raise ValueError(
            "At least two price observations are required."
        )

    returns: list[float] = []

    for previous, current in zip(prices, prices[1:]):
        if previous.close <= 0:
            raise ValueError(
                "Prices must be greater than zero."
            )

        daily_return = (
            current.close / previous.close
        ) - 1

        returns.append(daily_return)

    if not returns:
        raise ValueError(
            "At least one return observation is required."
        )

    mean = sum(returns) / len(returns)

    variance = sum(
        (value - mean) ** 2
        for value in returns
    ) / len(returns)

    standard_deviation = math.sqrt(variance)

    return standard_deviation * math.sqrt(252) * 100
