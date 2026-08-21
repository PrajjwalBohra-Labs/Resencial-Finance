from datetime import date

import pytest

from backend.app.schemas.market import HistoricalPrice
from backend.app.services.relationship_analysis_service import (
    RelationshipAnalysisService,
)


def create_prices(
    closes: list[float],
) -> list[HistoricalPrice]:
    return [
        HistoricalPrice(
            date=date(2026, 1, index + 1).isoformat(),
            open=close,
            high=close,
            low=close,
            close=close,
            volume=1000,
        )
        for index, close in enumerate(closes)
    ]


def test_relationship_service_aligns_dates() -> None:
    asset = create_prices([100, 102, 105, 108])
    benchmark = create_prices([100, 101, 103, 104])

    result = RelationshipAnalysisService.analyse(
        asset,
        benchmark,
        rolling_window=2,
    )

    assert result["observations"] == 4
    assert result["return_observations"] == 3
    assert result["correlation"] is not None
    assert result["beta"] is not None
    assert result["covariance"] is not None


def test_relationship_service_produces_rolling_correlation() -> None:
    asset = create_prices([100, 102, 104, 106, 108])
    benchmark = create_prices([100, 101, 102, 103, 104])

    result = RelationshipAnalysisService.analyse(
        asset,
        benchmark,
        rolling_window=2,
    )

    rolling = result["rolling_correlation"]

    assert isinstance(rolling, list)
    assert len(rolling) == 4
    assert rolling[0] is None


def test_relationship_service_produces_benchmark_comparison() -> None:
    asset = create_prices([100, 120])
    benchmark = create_prices([100, 110])

    result = RelationshipAnalysisService.analyse(
        asset,
        benchmark,
        rolling_window=2,
    )

    comparison = result["benchmark_comparison"]

    assert comparison["asset_return"] == pytest.approx(20.0)
    assert comparison["benchmark_return"] == pytest.approx(10.0)
    assert comparison["relative_performance"] == pytest.approx(10.0)

    # One return observation is insufficient for correlation,
    # covariance, or beta.
    assert result["correlation"] is None
    assert result["covariance"] is None
    assert result["beta"] is None


def test_relationship_service_requires_common_dates() -> None:
    asset = create_prices([100, 102])

    benchmark = [
        HistoricalPrice(
            date="2026-02-01",
            open=100,
            high=100,
            low=100,
            close=100,
            volume=1000,
        ),
        HistoricalPrice(
            date="2026-02-02",
            open=101,
            high=101,
            low=101,
            close=101,
            volume=1000,
        ),
    ]

    with pytest.raises(ValueError):
        RelationshipAnalysisService.analyse(
            asset,
            benchmark,
        )
