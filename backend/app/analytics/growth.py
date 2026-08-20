from __future__ import annotations

from datetime import date
from typing import Sequence


def calculate_period_growth(
    previous: float,
    current: float,
) -> float:
    if previous == 0:
        raise ValueError(
            "Previous value cannot be zero."
        )

    return ((current / previous) - 1) * 100


def calculate_growth_series(
    values: Sequence[float],
) -> list[float]:
    if len(values) < 2:
        return []

    growth: list[float] = []

    for previous, current in zip(values, values[1:]):
        growth.append(
            calculate_period_growth(
                previous,
                current,
            )
        )

    return growth


def calculate_growth_acceleration(
    values: Sequence[float],
) -> list[float]:
    """Measure change in growth rate between consecutive periods."""
    growth = calculate_growth_series(values)

    if len(growth) < 2:
        return []

    return [
        current - previous
        for previous, current in zip(
            growth,
            growth[1:],
        )
    ]


def calculate_cagr(
    values: Sequence[float],
    dates: Sequence[str] | None = None,
) -> float | None:
    if len(values) < 2:
        return None

    starting_value = float(values[0])
    ending_value = float(values[-1])

    if starting_value <= 0 or ending_value <= 0:
        raise ValueError(
            "CAGR values must be greater than zero."
        )

    if dates is None:
        years = len(values) - 1
    else:
        if len(dates) != len(values):
            raise ValueError(
                "Dates and values must have the same length."
            )

        start = date.fromisoformat(dates[0])
        end = date.fromisoformat(dates[-1])
        days = (end - start).days

        if days <= 0:
            raise ValueError(
                "Dates must span a positive period."
            )

        years = days / 365.25

    if years <= 0:
        return None

    return (
        ((ending_value / starting_value) ** (1 / years)) - 1
    ) * 100


def calculate_rolling_growth(
    values: Sequence[float],
    window: int,
) -> list[float | None]:
    if window < 2:
        raise ValueError(
            "Rolling growth window must be at least 2."
        )

    result: list[float | None] = []

    for index in range(len(values)):
        if index < window - 1:
            result.append(None)
            continue

        previous = float(values[index - window + 1])
        current = float(values[index])

        if previous == 0:
            result.append(None)
            continue

        result.append(
            calculate_period_growth(
                previous,
                current,
            )
        )

    return result


def calculate_trend_direction(
    values: Sequence[float],
) -> str:
    if len(values) < 2:
        return "insufficient_data"

    growth = calculate_growth_series(values)

    positive = sum(value > 0 for value in growth)
    negative = sum(value < 0 for value in growth)

    if positive == len(growth):
        return "consistently_rising"

    if negative == len(growth):
        return "consistently_declining"

    if positive > negative:
        return "mostly_rising"

    if negative > positive:
        return "mostly_declining"

    return "mixed"
