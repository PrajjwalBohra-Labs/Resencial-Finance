import pytest

from backend.app.analytics.relationships import (
    calculate_benchmark_comparison,
    calculate_beta,
    calculate_correlation,
    calculate_covariance,
    calculate_relative_performance,
    calculate_rolling_correlation,
)


def test_covariance() -> None:
    result = calculate_covariance(
        [1, 2, 3],
        [2, 4, 6],
    )

    assert result == pytest.approx(2.0)


def test_correlation_perfect_positive() -> None:
    result = calculate_correlation(
        [1, 2, 3, 4],
        [2, 4, 6, 8],
    )

    assert result == pytest.approx(1.0)


def test_correlation_perfect_negative() -> None:
    result = calculate_correlation(
        [1, 2, 3, 4],
        [8, 6, 4, 2],
    )

    assert result == pytest.approx(-1.0)


def test_rolling_correlation() -> None:
    result = calculate_rolling_correlation(
        [1, 2, 3, 4],
        [2, 4, 6, 8],
        window=3,
    )

    assert result[:2] == [None, None]
    assert result[2:] == pytest.approx([1.0, 1.0])


def test_beta() -> None:
    result = calculate_beta(
        [0.01, 0.02, 0.03, 0.04],
        [0.005, 0.01, 0.015, 0.02],
    )

    assert result == pytest.approx(2.0)


def test_relative_performance() -> None:
    result = calculate_relative_performance(
        100,
        120,
        100,
        110,
    )

    assert result == pytest.approx(10.0)


def test_benchmark_comparison() -> None:
    result = calculate_benchmark_comparison(
        100,
        120,
        100,
        110,
    )

    assert result["asset_return"] == pytest.approx(20.0)
    assert result["benchmark_return"] == pytest.approx(10.0)
    assert result["relative_performance"] == pytest.approx(10.0)


def test_correlation_rejects_mismatched_series() -> None:
    with pytest.raises(ValueError):
        calculate_correlation(
            [1, 2, 3],
            [1, 2],
        )


def test_beta_rejects_constant_benchmark() -> None:
    with pytest.raises(ValueError):
        calculate_beta(
            [0.01, 0.02, 0.03],
            [0.01, 0.01, 0.01],
        )
