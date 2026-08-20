from backend.app.domain.analytical_finding import (
    AnalyticalConfidence,
    AnalyticalDirection,
    AnalyticalFinding,
    AnalyticalFindingCategory,
)
from backend.app.domain.research import (
    ResearchContext,
    ResearchRequest,
)


def test_research_context_supports_analytical_findings() -> None:
    context = ResearchContext(
        request=ResearchRequest(
            question="Analyse revenue growth.",
            symbols=["HDFCBANK"],
            exchange="NSE",
        )
    )

    finding = AnalyticalFinding(
        finding="Revenue growth accelerated.",
        category=AnalyticalFindingCategory.TREND,
        metric="Revenue growth acceleration",
        value=6.3,
        unit="percentage_points",
        direction=AnalyticalDirection.POSITIVE,
        confidence=AnalyticalConfidence.HIGH,
        evidence_refs=["fundamental:HDFCBANK"],
    )

    context.add_finding(finding)

    assert len(context.analytical_findings) == 1
    assert (
        context.analytical_findings[0].metric
        == "Revenue growth acceleration"
    )


def test_analytical_finding_has_explicit_uncertainty() -> None:
    finding = AnalyticalFinding(
        finding="Revenue increased.",
        category=AnalyticalFindingCategory.GROWTH,
        metric="Revenue",
        uncertainty="Cause is not established.",
        known=["Observed revenue increase."],
        unknown=["Underlying cause."],
    )

    assert finding.uncertainty == "Cause is not established."
    assert finding.known == ["Observed revenue increase."]
    assert finding.unknown == ["Underlying cause."]
