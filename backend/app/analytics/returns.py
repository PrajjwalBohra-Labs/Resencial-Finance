from backend.app.schemas.market import (
    DailyPriceChange,
    HistoricalPrice,
    MarketPeriodSummary,
)


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


def calculate_daily_price_changes(
    prices: list[HistoricalPrice],
) -> list[DailyPriceChange]:
    if not prices:
        raise ValueError(
            "At least one price observation is required."
        )

    changes: list[DailyPriceChange] = []

    for price in prices:
        if price.open == 0:
            raise ValueError(
                "Opening price cannot be zero."
            )

        absolute_change = price.close - price.open
        percentage_change = (
            absolute_change / price.open
        ) * 100

        changes.append(
            DailyPriceChange(
                date=price.date,
                open_to_close_change=absolute_change,
                open_to_close_change_percentage=percentage_change,
            )
        )

    return changes


def calculate_market_period_summary(
    prices: list[HistoricalPrice],
) -> MarketPeriodSummary:
    if not prices:
        raise ValueError(
            "At least one price observation is required."
        )

    volumes = [price.volume for price in prices]
    highs = [price.high for price in prices]
    lows = [price.low for price in prices]

    return MarketPeriodSummary(
        period_high=max(highs),
        period_low=min(lows),
        total_volume=sum(volumes),
        average_daily_volume=sum(volumes) / len(volumes),
    )


