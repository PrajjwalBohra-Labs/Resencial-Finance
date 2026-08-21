from __future__ import annotations

import math
from typing import Sequence


def _clean_pair(
    first: Sequence[float],
    second: Sequence[float],
) -> tuple[list[float], list[float]]:
    if len(first) != len(second):
        raise ValueError("Series must have the same length.")

    if len(first) < 2:
        raise ValueError("At least two paired observations are required.")

    cleaned_first: list[float] = []
    cleaned_second: list[float] = []

    for first_value, second_value in zip(first, second):
        first_float = float(first_value)
        second_float = float(second_value)

        if not math.isfinite(first_float) or not math.isfinite(second_float):
            continue

        cleaned_first.append(first_float)
        cleaned_second.append(second_float)

    if len(cleaned_first) < 2:
        raise ValueError(
            "At least two finite paired observations are required."
        )

    return cleaned_first, cleaned_second


def calculate_covariance(
    first: Sequence[float],
    second: Sequence[float],
    *,
    sample: bool = True,
) -> float:
    """Calculate covariance between two aligned observations."""

    first_values, second_values = _clean_pair(first, second)

    first_mean = sum(first_values) / len(first_values)
    second_mean = sum(second_values) / len(second_values)

    divisor = len(first_values) - 1 if sample else len(first_values)

    return sum(
        (first_value - first_mean)
        * (second_value - second_mean)
        for first_value, second_value in zip(
            first_values,
            second_values,
        )
    ) / divisor


def calculate_correlation(
    first: Sequence[float],
    second: Sequence[float],
) -> float:
    """Calculate Pearson correlation between two aligned observations."""

    first_values, second_values = _clean_pair(first, second)

    first_mean = sum(first_values) / len(first_values)
    second_mean = sum(second_values) / len(second_values)

    first_deviations = [
        value - first_mean
        for value in first_values
    ]
    second_deviations = [
        value - second_mean
        for value in second_values
    ]

    first_variance = sum(
        deviation ** 2
        for deviation in first_deviations
    )
    second_variance = sum(
        deviation ** 2
        for deviation in second_deviations
    )

    if first_variance == 0 or second_variance == 0:
        raise ValueError(
            "Correlation is undefined for a constant series."
        )

    covariance = sum(
        first_deviation * second_deviation
        for first_deviation, second_deviation in zip(
            first_deviations,
            second_deviations,
        )
    )

    return covariance / math.sqrt(
        first_variance * second_variance
    )


def calculate_rolling_correlation(
    first: Sequence[float],
    second: Sequence[float],
    window: int,
) -> list[float | None]:
    """Calculate Pearson correlation over rolling aligned windows."""

    if window < 2:
        raise ValueError(
            "Rolling correlation window must be at least 2."
        )

    if len(first) != len(second):
        raise ValueError("Series must have the same length.")

    result: list[float | None] = []

    for index in range(len(first)):
        if index < window - 1:
            result.append(None)
            continue

        first_window = first[index - window + 1:index + 1]
        second_window = second[index - window + 1:index + 1]

        try:
            result.append(
                calculate_correlation(
                    first_window,
                    second_window,
                )
            )
        except ValueError:
            result.append(None)

    return result


def calculate_beta(
    asset_returns: Sequence[float],
    benchmark_returns: Sequence[float],
) -> float:
    """Calculate asset beta relative to benchmark returns."""

    asset_values, benchmark_values = _clean_pair(
        asset_returns,
        benchmark_returns,
    )

    benchmark_mean = sum(benchmark_values) / len(benchmark_values)

    benchmark_variance = sum(
        (value - benchmark_mean) ** 2
        for value in benchmark_values
    )

    if benchmark_variance == 0:
        raise ValueError(
            "Beta is undefined when benchmark variance is zero."
        )

    covariance = calculate_covariance(
        asset_values,
        benchmark_values,
        sample=True,
    )

    return covariance / (
        benchmark_variance / (len(benchmark_values) - 1)
    )


def calculate_relative_performance(
    asset_start: float,
    asset_end: float,
    benchmark_start: float,
    benchmark_end: float,
) -> float:
    """Return asset performance minus benchmark performance."""

    if asset_start == 0 or benchmark_start == 0:
        raise ValueError(
            "Starting values cannot be zero."
        )

    asset_return = (
        (asset_end / asset_start) - 1
    ) * 100

    benchmark_return = (
        (benchmark_end / benchmark_start) - 1
    ) * 100

    return asset_return - benchmark_return


def calculate_benchmark_comparison(
    asset_start: float,
    asset_end: float,
    benchmark_start: float,
    benchmark_end: float,
) -> dict[str, float]:
    """Return aligned absolute and relative performance metrics."""

    if asset_start == 0 or benchmark_start == 0:
        raise ValueError(
            "Starting values cannot be zero."
        )

    asset_return = (
        (asset_end / asset_start) - 1
    ) * 100

    benchmark_return = (
        (benchmark_end / benchmark_start) - 1
    ) * 100

    return {
        "asset_return": asset_return,
        "benchmark_return": benchmark_return,
        "relative_performance": asset_return - benchmark_return,
    }
