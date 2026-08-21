from __future__ import annotations

from backend.app.domain.analytical_finding import (
    AnalyticalConfidence,
    AnalyticalDirection,
    AnalyticalFinding,
    AnalyticalFindingCategory,
)


class RelationshipFindingService:
    """Converts deterministic relationship metrics into analytical findings."""

    @staticmethod
    def build(
        *,
        asset_symbol: str,
        benchmark_symbol: str,
        relationship: dict[str, object],
        asset_evidence_ref: str,
        benchmark_evidence_ref: str,
    ) -> list[AnalyticalFinding]:
        findings: list[AnalyticalFinding] = []

        correlation = relationship.get("correlation")

        if isinstance(correlation, (int, float)):
            direction = (
                AnalyticalDirection.POSITIVE
                if correlation > 0
                else AnalyticalDirection.NEGATIVE
                if correlation < 0
                else AnalyticalDirection.NEUTRAL
            )

            findings.append(
                AnalyticalFinding(
                    finding=(
                        f"{asset_symbol} has a Pearson return correlation "
                        f"of {correlation:.4f} with {benchmark_symbol}."
                    ),
                    category=AnalyticalFindingCategory.RELATIONSHIP,
                    metric=f"{asset_symbol} correlation with {benchmark_symbol}",
                    value=float(correlation),
                    direction=direction,
                    confidence=AnalyticalConfidence.HIGH,
                    significance=(
                        "Correlation measures linear co-movement between "
                        "the aligned return observations."
                    ),
                    methodology=(
                        "Pearson correlation calculated from aligned "
                        "period-over-period returns."
                    ),
                    evidence_refs=[
                        asset_evidence_ref,
                        benchmark_evidence_ref,
                    ],
                    uncertainty=(
                        "Correlation describes the supplied observation "
                        "window and does not establish causation or future "
                        "co-movement."
                    ),
                    known=[
                        f"Observed correlation: {correlation:.4f}.",
                        f"Benchmark: {benchmark_symbol}.",
                    ],
                    unknown=[
                        "Future correlation.",
                        "Causal relationship between the instruments.",
                    ],
                )
            )

        beta = relationship.get("beta")

        if isinstance(beta, (int, float)):
            direction = (
                AnalyticalDirection.POSITIVE
                if beta > 0
                else AnalyticalDirection.NEGATIVE
                if beta < 0
                else AnalyticalDirection.NEUTRAL
            )

            findings.append(
                AnalyticalFinding(
                    finding=(
                        f"{asset_symbol} has a beta of "
                        f"{float(beta):.4f} relative to {benchmark_symbol}."
                    ),
                    category=AnalyticalFindingCategory.RELATIONSHIP,
                    metric=f"{asset_symbol} beta versus {benchmark_symbol}",
                    value=float(beta),
                    direction=direction,
                    confidence=AnalyticalConfidence.HIGH,
                    significance=(
                        "Beta measures the asset's historical return "
                        "sensitivity relative to benchmark returns."
                    ),
                    methodology=(
                        "Covariance of asset and benchmark returns divided "
                        "by benchmark return variance."
                    ),
                    evidence_refs=[
                        asset_evidence_ref,
                        benchmark_evidence_ref,
                    ],
                    uncertainty=(
                        "Beta is historical and depends on the selected "
                        "observation window."
                    ),
                    known=[
                        f"Observed beta: {float(beta):.4f}.",
                        f"Benchmark: {benchmark_symbol}.",
                    ],
                    unknown=[
                        "Future beta.",
                        "Whether the historical sensitivity persists.",
                    ],
                )
            )

        covariance = relationship.get("covariance")

        if isinstance(covariance, (int, float)):
            direction = (
                AnalyticalDirection.POSITIVE
                if covariance > 0
                else AnalyticalDirection.NEGATIVE
                if covariance < 0
                else AnalyticalDirection.NEUTRAL
            )

            findings.append(
                AnalyticalFinding(
                    finding=(
                        f"{asset_symbol} has return covariance of "
                        f"{float(covariance):.6f} with {benchmark_symbol}."
                    ),
                    category=AnalyticalFindingCategory.RELATIONSHIP,
                    metric=(
                        f"{asset_symbol} return covariance with "
                        f"{benchmark_symbol}"
                    ),
                    value=float(covariance),
                    direction=direction,
                    confidence=AnalyticalConfidence.HIGH,
                    significance=(
                        "Covariance describes the joint directional "
                        "variation of the aligned returns."
                    ),
                    methodology=(
                        "Sample covariance of aligned asset and benchmark "
                        "period-over-period returns."
                    ),
                    evidence_refs=[
                        asset_evidence_ref,
                        benchmark_evidence_ref,
                    ],
                    uncertainty=(
                        "Covariance depends on return units and the selected "
                        "observation window."
                    ),
                    known=[
                        f"Observed covariance: {float(covariance):.6f}.",
                    ],
                    unknown=[
                        "Future covariance.",
                    ],
                )
            )

        comparison = relationship.get("benchmark_comparison")

        if isinstance(comparison, dict):
            asset_return = comparison.get("asset_return")
            benchmark_return = comparison.get("benchmark_return")
            relative_performance = comparison.get("relative_performance")

            if (
                isinstance(asset_return, (int, float))
                and isinstance(benchmark_return, (int, float))
                and isinstance(relative_performance, (int, float))
            ):
                direction = (
                    AnalyticalDirection.POSITIVE
                    if relative_performance > 0
                    else AnalyticalDirection.NEGATIVE
                    if relative_performance < 0
                    else AnalyticalDirection.NEUTRAL
                )

                findings.append(
                    AnalyticalFinding(
                        finding=(
                            f"{asset_symbol} returned "
                            f"{float(asset_return):.4f}% versus "
                            f"{float(benchmark_return):.4f}% for "
                            f"{benchmark_symbol}, a relative performance "
                            f"difference of "
                            f"{float(relative_performance):.4f} "
                            f"percentage points."
                        ),
                        category=AnalyticalFindingCategory.RELATIONSHIP,
                        metric=(
                            f"{asset_symbol} relative performance versus "
                            f"{benchmark_symbol}"
                        ),
                        value=float(relative_performance),
                        unit="percentage_points",
                        direction=direction,
                        confidence=AnalyticalConfidence.HIGH,
                        significance=(
                            "Relative performance compares cumulative "
                            "asset and benchmark returns over the supplied "
                            "period."
                        ),
                        methodology=(
                            "Asset percentage return minus benchmark "
                            "percentage return."
                        ),
                        evidence_refs=[
                            asset_evidence_ref,
                            benchmark_evidence_ref,
                        ],
                        uncertainty=(
                            "The comparison is limited to the supplied "
                            "start and end observations."
                        ),
                        known=[
                            f"Asset return: {float(asset_return):.4f}%.",
                            (
                                f"Benchmark return: "
                                f"{float(benchmark_return):.4f}%."
                            ),
                            (
                                f"Relative performance: "
                                f"{float(relative_performance):.4f} "
                                f"percentage points."
                            ),
                        ],
                        unknown=[
                            "Future relative performance.",
                        ],
                    )
                )

        return findings
