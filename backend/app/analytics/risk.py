import math
from datetime import date

from backend.app.schemas.market import HistoricalPrice


def calculate_cagr(
    prices: list[HistoricalPrice],
) -> float | None:
    """Calculate CAGR when the observation period spans at least one year."""
    if len(prices) < 2:
        return None

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

    if days < 365:
        return None

    years = days / 365.25

    if years <= 0:
        return None

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
) -> float | None:
    """Calculate annualised volatility with sufficient return observations."""
    if len(prices) < 3:
        return None

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

    if len(returns) < 2:
        return None

    mean = sum(returns) / len(returns)

    variance = sum(
        (value - mean) ** 2
        for value in returns
    ) / (len(returns) - 1)

    standard_deviation = math.sqrt(variance)

    return standard_deviation * math.sqrt(252) * 100
