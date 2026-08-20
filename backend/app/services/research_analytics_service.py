from __future__ import annotations

from backend.app.analytics import (
    calculate_distribution_summary,
    calculate_growth_series,
    calculate_trend_direction,
)
from backend.app.analytics.findings import generate_growth_findings
from backend.app.domain.analytical_finding import (
    AnalyticalConfidence,
    AnalyticalDirection,
    AnalyticalFinding,
    AnalyticalFindingCategory,
)
from backend.app.schemas.market import HistoricalPrice


class ResearchAnalyticsService:
    """Generates deterministic analytical findings from market observations."""

    @staticmethod
    def analyse_prices(
        *,
        symbol: str,
        prices: list[HistoricalPrice],
    ) -> list[AnalyticalFinding]:
        if len(prices) < 2:
            return []

        evidence_ref = f"market:{symbol}"

        closes = [float(price.close) for price in prices]
        periods = [price.date for price in prices]

        findings: list[AnalyticalFinding] = []

        findings.extend(
            generate_growth_findings(
                metric=f"{symbol} closing price",
                values=closes,
                periods=periods,
                evidence_ref=evidence_ref,
            )
        )

        findings.extend(
            ResearchAnalyticsService._build_trend_finding(
                symbol=symbol,
                closes=closes,
                evidence_ref=evidence_ref,
            )
        )

        findings.extend(
            ResearchAnalyticsService._build_distribution_findings(
                symbol=symbol,
                closes=closes,
                evidence_ref=evidence_ref,
            )
        )

        return findings

    @staticmethod
    def _build_trend_finding(
        *,
        symbol: str,
        closes: list[float],
        evidence_ref: str,
    ) -> list[AnalyticalFinding]:
        trend = calculate_trend_direction(closes)

        if trend == "insufficient_data":
            return []

        direction_map = {
            "consistently_rising": AnalyticalDirection.POSITIVE,
            "mostly_rising": AnalyticalDirection.POSITIVE,
            "consistently_declining": AnalyticalDirection.NEGATIVE,
            "mostly_declining": AnalyticalDirection.NEGATIVE,
            "mixed": AnalyticalDirection.MIXED,
        }

        return [
            AnalyticalFinding(
                finding=(
                    f"{symbol} closing-price trend is {trend.replace('_', ' ')}."
                ),
                category=AnalyticalFindingCategory.TREND,
                metric=f"{symbol} price trend",
                direction=direction_map[trend],
                confidence=AnalyticalConfidence.HIGH,
                significance=(
                    "Trend classification is derived from the supplied "
                    "sequence of closing prices."
                ),
                methodology=(
                    "Period-over-period closing-price growth direction."
                ),
                evidence_refs=[evidence_ref],
                uncertainty=(
                    "Trend classification describes the supplied period "
                    "and does not establish future direction."
                ),
                known=[
                    f"Observed closing prices for {len(closes)} periods.",
                    f"Trend classification: {trend}.",
                ],
                unknown=[
                    "Future price direction.",
                    "Underlying causes of the observed trend.",
                ],
            )
        ]

    @staticmethod
    def _build_distribution_findings(
        *,
        symbol: str,
        closes: list[float],
        evidence_ref: str,
    ) -> list[AnalyticalFinding]:
        growth = calculate_growth_series(closes)

        if len(growth) < 2:
            return []

        summary = calculate_distribution_summary(growth)

        findings: list[AnalyticalFinding] = []

        findings.append(
            AnalyticalFinding(
                finding=(
                    f"{symbol} period-over-period growth has a mean of "
                    f"{summary['mean']:.4f}% and a median of "
                    f"{summary['median']:.4f}%."
                ),
                category=AnalyticalFindingCategory.DISTRIBUTION,
                metric=f"{symbol} growth distribution",
                value=summary["mean"],
                unit="percent",
                direction=(
                    AnalyticalDirection.POSITIVE
                    if summary["mean"] > 0
                    else AnalyticalDirection.NEGATIVE
                    if summary["mean"] < 0
                    else AnalyticalDirection.NEUTRAL
                ),
                confidence=AnalyticalConfidence.HIGH,
                significance=(
                    "Mean and median summarize the central tendency of "
                    "period-over-period growth."
                ),
                methodology=(
                    "Arithmetic mean and median of deterministic growth "
                    "observations."
                ),
                evidence_refs=[evidence_ref],
                uncertainty=(
                    "The distribution is descriptive and does not establish "
                    "a predictive relationship."
                ),
                known=[
                    f"Mean growth: {summary['mean']:.4f}%.",
                    f"Median growth: {summary['median']:.4f}%.",
                    f"Observations: {int(summary['count'])}.",
                ],
                unknown=[
                    "Future return distribution.",
                    "External causes of individual observations.",
                ],
            )
        )

        if summary["standard_deviation"] is not None:
            findings.append(
                AnalyticalFinding(
                    finding=(
                        f"{symbol} growth has a standard deviation of "
                        f"{summary['standard_deviation']:.4f}%."
                    ),
                    category=AnalyticalFindingCategory.RISK,
                    metric=f"{symbol} growth standard deviation",
                    value=summary["standard_deviation"],
                    unit="percent",
                    direction=AnalyticalDirection.NEUTRAL,
                    confidence=AnalyticalConfidence.HIGH,
                    significance=(
                        "Standard deviation measures dispersion around "
                        "the mean growth rate."
                    ),
                    methodology="Sample standard deviation of growth observations.",
                    evidence_refs=[evidence_ref],
                    uncertainty=(
                        "Dispersion depends on the selected observation "
                        "window and may change across regimes."
                    ),
                    known=[
                        f"Growth standard deviation: "
                        f"{summary['standard_deviation']:.4f}%.",
                    ],
                    unknown=[
                        "Future volatility.",
                        "Whether the observed dispersion persists.",
                    ],
                )
            )

        if summary["skewness"] is not None:
            findings.append(
                AnalyticalFinding(
                    finding=(
                        f"{symbol} growth distribution has skewness of "
                        f"{summary['skewness']:.4f}."
                    ),
                    category=AnalyticalFindingCategory.DISTRIBUTION,
                    metric=f"{symbol} growth skewness",
                    value=summary["skewness"],
                    direction=(
                        AnalyticalDirection.POSITIVE
                        if summary["skewness"] > 0
                        else AnalyticalDirection.NEGATIVE
                        if summary["skewness"] < 0
                        else AnalyticalDirection.NEUTRAL
                    ),
                    confidence=AnalyticalConfidence.MEDIUM,
                    significance=(
                        "Skewness describes asymmetry in the observed "
                        "growth distribution."
                    ),
                    methodology="Third standardized central moment.",
                    evidence_refs=[evidence_ref],
                    uncertainty=(
                        "Skewness can be unstable with short samples."
                    ),
                    known=[
                        f"Observed skewness: {summary['skewness']:.4f}.",
                    ],
                    unknown=[
                        "Whether the distribution shape persists.",
                    ],
                )
            )

        if summary["kurtosis"] is not None:
            findings.append(
                AnalyticalFinding(
                    finding=(
                        f"{symbol} growth distribution has excess kurtosis "
                        f"of {summary['kurtosis']:.4f}."
                    ),
                    category=AnalyticalFindingCategory.DISTRIBUTION,
                    metric=f"{symbol} growth kurtosis",
                    value=summary["kurtosis"],
                    direction=(
                        AnalyticalDirection.POSITIVE
                        if summary["kurtosis"] > 0
                        else AnalyticalDirection.NEGATIVE
                        if summary["kurtosis"] < 0
                        else AnalyticalDirection.NEUTRAL
                    ),
                    confidence=AnalyticalConfidence.MEDIUM,
                    significance=(
                        "Excess kurtosis describes tail heaviness relative "
                        "to a normal distribution."
                    ),
                    methodology="Fourth standardized central moment minus three.",
                    evidence_refs=[evidence_ref],
                    uncertainty=(
                        "Kurtosis estimates can be unstable with short "
                        "time series."
                    ),
                    known=[
                        f"Observed excess kurtosis: "
                        f"{summary['kurtosis']:.4f}.",
                    ],
                    unknown=[
                        "Future tail behavior.",
                    ],
                )
            )

        return findings
