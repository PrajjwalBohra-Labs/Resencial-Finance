from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)
from backend.app.domain.research import (
    ResearchContext,
    ResearchFocus,
    ResearchRequest,
)


def create_evidence() -> Evidence:
    return Evidence(
        evidence_type=EvidenceType.MARKET_DATA,
        title="HDFC Bank market data",
        content="Historical NSE market data.",
        source=EvidenceSource(
            name="Yahoo Finance",
            retrieved_at=datetime.now(timezone.utc),
            provider="yahoo_finance",
        ),
        symbol="HDFCBANK",
        exchange="NSE",
    )


def test_research_request_defaults_to_general() -> None:
    request = ResearchRequest(
        question="Analyse HDFC Bank.",
    )

    assert request.question == "Analyse HDFC Bank."
    assert request.symbols == []
    assert request.exchange is None
    assert request.focus == ResearchFocus.GENERAL


def test_research_request_normal_research_query() -> None:
    request = ResearchRequest(
        question="Analyse the valuation and risks of HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        focus=ResearchFocus.VALUATION,
    )

    assert request.symbols == ["HDFCBANK"]
    assert request.exchange == "NSE"
    assert request.focus == ResearchFocus.VALUATION


def test_research_request_rejects_empty_question() -> None:
    with pytest.raises(ValidationError):
        ResearchRequest(question="")


def test_research_context_starts_without_evidence() -> None:
    context = ResearchContext(
        request=ResearchRequest(
            question="Research HDFC Bank.",
            symbols=["HDFCBANK"],
            exchange="NSE",
        )
    )

    assert context.evidence == []


def test_research_context_can_add_evidence() -> None:
    context = ResearchContext(
        request=ResearchRequest(
            question="Research HDFC Bank.",
            symbols=["HDFCBANK"],
            exchange="NSE",
        )
    )

    evidence = create_evidence()

    context.add_evidence(evidence)

    assert len(context.evidence) == 1
    assert context.evidence[0].symbol == "HDFCBANK"
    assert context.evidence[0].evidence_type == EvidenceType.MARKET_DATA


def test_research_context_supports_multiple_evidence_items() -> None:
    context = ResearchContext(
        request=ResearchRequest(
            question="Research HDFC Bank.",
            symbols=["HDFCBANK"],
            exchange="NSE",
        ),
        evidence=[
            create_evidence(),
            create_evidence(),
        ],
    )

    assert len(context.evidence) == 2


def test_research_context_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ResearchContext(
            request=ResearchRequest(
                question="Research HDFC Bank.",
            ),
            unexpected_field="not allowed",
        )
