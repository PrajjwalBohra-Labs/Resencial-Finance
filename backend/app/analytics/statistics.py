from __future__ import annotations

import math
from statistics import fmean, median
from typing import Sequence


def _clean(values: Sequence[float]) -> list[float]:
    cleaned = [
        float(value)
        for value in values
        if math.isfinite(float(value))
    ]

    if not cleaned:
        raise ValueError("At least one finite observation is required.")

    return cleaned


def calculate_mean(values: Sequence[float]) -> float:
    return fmean(_clean(values))


def calculate_median(values: Sequence[float]) -> float:
    return median(_clean(values))


def calculate_standard_deviation(
    values: Sequence[float],
    *,
    sample: bool = True,
) -> float:
    cleaned = _clean(values)

    if sample and len(cleaned) < 2:
        raise ValueError(
            "At least two observations are required for sample standard deviation."
        )

    mean = fmean(cleaned)
    divisor = len(cleaned) - 1 if sample else len(cleaned)

    return math.sqrt(
        sum((value - mean) ** 2 for value in cleaned) / divisor
    )


def calculate_percentile(
    values: Sequence[float],
    percentile: float,
) -> float:
    if not 0 <= percentile <= 100:
        raise ValueError("Percentile must be between 0 and 100.")

    cleaned = sorted(_clean(values))

    if len(cleaned) == 1:
        return cleaned[0]

    position = (len(cleaned) - 1) * percentile / 100
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return cleaned[lower]

    weight = position - lower

    return (
        cleaned[lower]
        + (cleaned[upper] - cleaned[lower]) * weight
    )


def calculate_skewness(values: Sequence[float]) -> float | None:
    cleaned = _clean(values)

    if len(cleaned) < 3:
        return None

    mean = fmean(cleaned)

    deviations = [
        value - mean
        for value in cleaned
    ]

    second_moment = fmean(
        deviation ** 2
        for deviation in deviations
    )

    if second_moment == 0:
        return 0.0

    third_moment = fmean(
        deviation ** 3
        for deviation in deviations
    )

    return third_moment / (second_moment ** 1.5)


def calculate_kurtosis(
    values: Sequence[float],
) -> float | None:
    """Return excess kurtosis.

    A normal distribution therefore has kurtosis approximately 0.
    """
    cleaned = _clean(values)

    if len(cleaned) < 4:
        return None

    mean = fmean(cleaned)

    deviations = [
        value - mean
        for value in cleaned
    ]

    second_moment = fmean(
        deviation ** 2
        for deviation in deviations
    )

    if second_moment == 0:
        return 0.0

    fourth_moment = fmean(
        deviation ** 4
        for deviation in deviations
    )

    return (fourth_moment / (second_moment ** 2)) - 3.0


def calculate_distribution_summary(
    values: Sequence[float],
) -> dict[str, float | None]:
    cleaned = _clean(values)

    return {
        "count": float(len(cleaned)),
        "mean": calculate_mean(cleaned),
        "median": calculate_median(cleaned),
        "standard_deviation": (
            calculate_standard_deviation(cleaned)
            if len(cleaned) >= 2
            else None
        ),
        "minimum": min(cleaned),
        "maximum": max(cleaned),
        "percentile_5": calculate_percentile(cleaned, 5),
        "percentile_25": calculate_percentile(cleaned, 25),
        "percentile_50": calculate_percentile(cleaned, 50),
        "percentile_75": calculate_percentile(cleaned, 75),
        "percentile_95": calculate_percentile(cleaned, 95),
        "skewness": calculate_skewness(cleaned),
        "kurtosis": calculate_kurtosis(cleaned),
    }
