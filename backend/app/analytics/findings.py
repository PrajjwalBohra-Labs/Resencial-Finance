from __future__ import annotations

from backend.app.analytics.growth import (
    calculate_growth_acceleration,
    calculate_growth_series,
)
from backend.app.domain.analytical_finding import (
    AnalyticalConfidence,
    AnalyticalDirection,
    AnalyticalFinding,
    AnalyticalFindingCategory,
)


def generate_growth_findings(
    *,
    metric: str,
    values: list[float],
    periods: list[str],
    evidence_ref: str,
) -> list[AnalyticalFinding]:
    if len(values) < 2:
        return []

    if len(values) != len(periods):
        raise ValueError(
            "Values and periods must have the same length."
        )

    growth = calculate_growth_series(values)
    findings: list[AnalyticalFinding] = []

    latest_growth = growth[-1]

    if latest_growth > 0:
        direction = AnalyticalDirection.POSITIVE
    elif latest_growth < 0:
        direction = AnalyticalDirection.NEGATIVE
    else:
        direction = AnalyticalDirection.NEUTRAL

    findings.append(
        AnalyticalFinding(
            finding=(
                f"{metric} changed by {latest_growth:.4f}% "
                f"between {periods[-2]} and {periods[-1]}."
            ),
            category=AnalyticalFindingCategory.GROWTH,
            metric=metric,
            value=latest_growth,
            unit="percent",
            direction=direction,
            confidence=AnalyticalConfidence.HIGH,
            significance=(
                "Latest period-over-period change derived "
                "directly from supplied observations."
            ),
            methodology="Period-over-period percentage growth.",
            evidence_refs=[evidence_ref],
            uncertainty=(
                "The finding describes the observed period only "
                "and does not establish causation."
            ),
            known=[
                f"Observed {metric} values for supplied periods.",
                f"Latest growth rate: {latest_growth:.4f}%.",
            ],
            unknown=[
                "Underlying causes of the change.",
                "Future growth trajectory.",
            ],
        )
    )

    acceleration = calculate_growth_acceleration(values)

    if acceleration:
        latest_acceleration = acceleration[-1]

        if latest_acceleration > 0:
            acceleration_direction = AnalyticalDirection.POSITIVE
            description = "accelerated"
        elif latest_acceleration < 0:
            acceleration_direction = AnalyticalDirection.NEGATIVE
            description = "decelerated"
        else:
            acceleration_direction = AnalyticalDirection.NEUTRAL
            description = "remained stable"

        findings.append(
            AnalyticalFinding(
                finding=(
                    f"{metric} growth {description} by "
                    f"{abs(latest_acceleration):.4f} percentage points "
                    f"versus the preceding growth period."
                ),
                category=AnalyticalFindingCategory.TREND,
                metric=f"{metric} growth acceleration",
                value=latest_acceleration,
                unit="percentage_points",
                direction=acceleration_direction,
                confidence=AnalyticalConfidence.HIGH,
                significance=(
                    "Measures the change in the growth rate itself, "
                    "rather than only the latest growth rate."
                ),
                methodology=(
                    "Difference between consecutive "
                    "period-over-period growth rates."
                ),
                evidence_refs=[evidence_ref],
                uncertainty=(
                    "Acceleration can be sensitive to short "
                    "time series and unusually small prior values."
                ),
                known=[
                    f"Latest growth-rate change: "
                    f"{latest_acceleration:.4f} percentage points."
                ],
                unknown=[
                    "Whether the acceleration persists.",
                    "Economic or operational causes.",
                ],
            )
        )

    return findings
