import pytest

from backend.app.analytics.findings import generate_growth_findings
from backend.app.domain.analytical_finding import (
    AnalyticalConfidence,
    AnalyticalDirection,
    AnalyticalFindingCategory,
)


def test_growth_finding_contains_deterministic_evidence() -> None:
    findings = generate_growth_findings(
        metric="Revenue",
        values=[100, 110, 132],
        periods=[
            "2024-03-31",
            "2025-03-31",
            "2026-03-31",
        ],
        evidence_ref="fundamental:HDFCBANK",
    )

    assert len(findings) == 2

    growth = findings[0]

    assert growth.category == AnalyticalFindingCategory.GROWTH
    assert growth.metric == "Revenue"
    assert growth.value == pytest.approx(20.0)
    assert growth.unit == "percent"
    assert growth.direction == AnalyticalDirection.POSITIVE
    assert growth.confidence == AnalyticalConfidence.HIGH
    assert "fundamental:HDFCBANK" in growth.evidence_refs
    assert growth.known
    assert growth.unknown


def test_growth_acceleration_finding() -> None:
    findings = generate_growth_findings(
        metric="Revenue",
        values=[100, 110, 132],
        periods=[
            "2024-03-31",
            "2025-03-31",
            "2026-03-31",
        ],
        evidence_ref="fundamental:HDFCBANK",
    )

    acceleration = findings[1]

    assert acceleration.category == AnalyticalFindingCategory.TREND
    assert acceleration.metric == "Revenue growth acceleration"
    assert acceleration.value == pytest.approx(10.0)
    assert acceleration.unit == "percentage_points"
    assert acceleration.direction == AnalyticalDirection.POSITIVE
    assert acceleration.confidence == AnalyticalConfidence.HIGH


def test_declining_growth_direction() -> None:
    findings = generate_growth_findings(
        metric="Net Income",
        values=[100, 150, 120],
        periods=[
            "2024-03-31",
            "2025-03-31",
            "2026-03-31",
        ],
        evidence_ref="fundamental:ETERNAL",
    )

    assert findings[0].value == pytest.approx(-20.0)
    assert findings[0].direction == AnalyticalDirection.NEGATIVE

    assert findings[1].value == pytest.approx(-70.0)
    assert findings[1].direction == AnalyticalDirection.NEGATIVE


def test_insufficient_history_produces_no_findings() -> None:
    findings = generate_growth_findings(
        metric="Revenue",
        values=[100],
        periods=["2026-03-31"],
        evidence_ref="fundamental:HDFCBANK",
    )

    assert findings == []


def test_values_and_periods_must_match() -> None:
    with pytest.raises(ValueError):
        generate_growth_findings(
            metric="Revenue",
            values=[100, 110],
            periods=["2026-03-31"],
            evidence_ref="fundamental:HDFCBANK",
        )
