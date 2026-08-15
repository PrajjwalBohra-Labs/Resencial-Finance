from backend.app.schemas.market import HistoricalPrice


def calculate_absolute_return(
    prices: list[HistoricalPrice],
) -> float:
    if len(prices) < 2:
        raise ValueError(
            "At least two price observations are required."
        )

    return prices[-1].close - prices[0].close


def calculate_percentage_return(
    prices: list[HistoricalPrice],
) -> float:
    if len(prices) < 2:
        raise ValueError(
            "At least two price observations are required."
        )

    starting_price = prices[0].close

    if starting_price == 0:
        raise ValueError(
            "Starting price cannot be zero."
        )

    return (
        (prices[-1].close - starting_price)
        / starting_price
    ) * 100


def calculate_price_summary(
    prices: list[HistoricalPrice],
) -> dict[str, float]:
    if not prices:
        raise ValueError(
            "At least one price observation is required."
        )

    closing_prices = [price.close for price in prices]

    return {
        "starting_price": closing_prices[0],
        "latest_price": closing_prices[-1],
        "highest_close": max(closing_prices),
        "lowest_close": min(closing_prices),
    }
