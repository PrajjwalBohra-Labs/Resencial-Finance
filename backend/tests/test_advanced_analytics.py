import pytest

from backend.app.analytics.growth import (
    calculate_cagr,
    calculate_growth_acceleration,
    calculate_growth_series,
    calculate_period_growth,
    calculate_rolling_growth,
    calculate_trend_direction,
)
from backend.app.analytics.statistics import (
    calculate_distribution_summary,
    calculate_kurtosis,
    calculate_mean,
    calculate_median,
    calculate_percentile,
    calculate_skewness,
    calculate_standard_deviation,
)


def test_period_growth() -> None:
    assert calculate_period_growth(100, 120) == pytest.approx(20.0)


def test_growth_series() -> None:
    result = calculate_growth_series([100, 110, 121])

    assert result == pytest.approx([10.0, 10.0])


def test_growth_acceleration() -> None:
    result = calculate_growth_acceleration([100, 110, 132])

    assert result == pytest.approx([10.0])


def test_cagr_with_dates() -> None:
    result = calculate_cagr(
        [100, 121],
        ["2024-01-01", "2026-01-01"],
    )

    assert result == pytest.approx(10.0, rel=0.01)


def test_rolling_growth() -> None:
    result = calculate_rolling_growth(
        [100, 110, 121, 133.1],
        window=2,
    )

    assert result[0] is None
    assert result[1] == pytest.approx(10.0)
    assert result[2] == pytest.approx(10.0)
    assert result[3] == pytest.approx(10.0)


def test_trend_direction() -> None:
    assert (
        calculate_trend_direction([100, 110, 120])
        == "consistently_rising"
    )

    assert (
        calculate_trend_direction([120, 110, 100])
        == "consistently_declining"
    )


def test_mean_and_median() -> None:
    values = [1, 2, 3, 4, 5]

    assert calculate_mean(values) == pytest.approx(3)
    assert calculate_median(values) == pytest.approx(3)


def test_standard_deviation() -> None:
    result = calculate_standard_deviation(
        [1, 2, 3, 4, 5]
    )

    assert result == pytest.approx(1.58113883)


def test_percentile_interpolation() -> None:
    assert calculate_percentile(
        [1, 2, 3, 4],
        50,
    ) == pytest.approx(2.5)


def test_skewness_symmetric_distribution() -> None:
    result = calculate_skewness(
        [1, 2, 3, 4, 5]
    )

    assert result == pytest.approx(0.0)


def test_kurtosis_constant_distribution() -> None:
    result = calculate_kurtosis(
        [5, 5, 5, 5]
    )

    assert result == pytest.approx(0.0)


def test_distribution_summary() -> None:
    result = calculate_distribution_summary(
        [1, 2, 3, 4, 5]
    )

    assert result["count"] == 5.0
    assert result["mean"] == pytest.approx(3)
    assert result["median"] == pytest.approx(3)
    assert result["minimum"] == 1
    assert result["maximum"] == 5
    assert result["percentile_25"] == pytest.approx(2)
    assert result["percentile_75"] == pytest.approx(4)
    assert result["skewness"] == pytest.approx(0)


def test_growth_rejects_zero_previous_value() -> None:
    with pytest.raises(ValueError):
        calculate_period_growth(0, 100)


def test_cagr_rejects_non_positive_values() -> None:
    with pytest.raises(ValueError):
        calculate_cagr([0, 100])


def test_rolling_growth_rejects_invalid_window() -> None:
    with pytest.raises(ValueError):
        calculate_rolling_growth([1, 2, 3], 1)
