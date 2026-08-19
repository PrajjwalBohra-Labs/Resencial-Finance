from datetime import date, datetime, timezone

import pytest

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)
from backend.app.retrieval import (
    EvidenceRetriever,
    RetrievalQuery,
)


def make_evidence(
    *,
    evidence_type: EvidenceType,
    content: str,
    symbol: str = "HDFCBANK",
    exchange: str = "NSE",
) -> Evidence:
    return Evidence(
        evidence_type=evidence_type,
        title=f"{symbol} evidence",
        content=content,
        source=EvidenceSource(
            name="test_source",
            provider="test_provider",
            retrieved_at=datetime(
                2026,
                8,
                19,
                tzinfo=timezone.utc,
            ),
        ),
        symbol=symbol,
        exchange=exchange,
        confidence=1.0,
    )


@pytest.mark.asyncio
async def test_retriever_prioritizes_matching_symbol() -> None:
    retriever = EvidenceRetriever()

    evidence = [
        make_evidence(
            evidence_type=EvidenceType.FUNDAMENTAL,
            content=(
                "HDFCBANK revenue increased 20% "
                "during the latest financial period."
            ),
            symbol="HDFCBANK",
        ),
        make_evidence(
            evidence_type=EvidenceType.FUNDAMENTAL,
            content=(
                "ICICIBANK revenue increased 18% "
                "during the latest financial period."
            ),
            symbol="ICICIBANK",
        ),
    ]

    result = await retriever.retrieve(
        RetrievalQuery(
            question="Analyse HDFCBANK revenue growth.",
            symbols=["HDFCBANK"],
            exchange="NSE",
        ),
        evidence,
    )

    assert result.evidence_count == 1
    assert result.chunks[0].symbol == "HDFCBANK"


@pytest.mark.asyncio
async def test_retriever_filters_evidence_type() -> None:
    retriever = EvidenceRetriever()

    evidence = [
        make_evidence(
            evidence_type=EvidenceType.MARKET_DATA,
            content=(
                "HDFCBANK price declined by 2% "
                "during the trading period."
            ),
        ),
        make_evidence(
            evidence_type=EvidenceType.FUNDAMENTAL,
            content=(
                "HDFCBANK revenue increased by 20%."
            ),
        ),
    ]

    result = await retriever.retrieve(
        RetrievalQuery(
            question="Analyse HDFCBANK fundamentals.",
            symbols=["HDFCBANK"],
            evidence_types=[EvidenceType.FUNDAMENTAL],
        ),
        evidence,
    )

    assert result.evidence_count == 1
    assert (
        result.chunks[0].evidence_type
        == EvidenceType.FUNDAMENTAL
    )


@pytest.mark.asyncio
async def test_retriever_filters_observation_date() -> None:
    retriever = EvidenceRetriever()

    evidence = [
        make_evidence(
            evidence_type=EvidenceType.MARKET_DATA,
            content=(
                "Market observations for 2026-08-10. "
                "HDFCBANK closed at 731."
            ),
        ),
        make_evidence(
            evidence_type=EvidenceType.MARKET_DATA,
            content=(
                "Market observations for 2026-08-20. "
                "HDFCBANK closed at 740."
            ),
        ),
    ]

    result = await retriever.retrieve(
        RetrievalQuery(
            question="What happened to HDFCBANK?",
            symbols=["HDFCBANK"],
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 15),
        ),
        evidence,
    )

    assert result.evidence_count == 1
    assert "2026-08-10" in result.chunks[0].text


@pytest.mark.asyncio
async def test_retriever_returns_ranked_results() -> None:
    retriever = EvidenceRetriever()

    evidence = [
        make_evidence(
            evidence_type=EvidenceType.FUNDAMENTAL,
            content="HDFCBANK revenue.",
        ),
        make_evidence(
            evidence_type=EvidenceType.FUNDAMENTAL,
            content=(
                "HDFCBANK revenue growth, earnings growth, "
                "profitability and EPS analysis."
            ),
        ),
    ]

    result = await retriever.retrieve(
        RetrievalQuery(
            question=(
                "Analyse HDFCBANK revenue growth "
                "earnings profitability and EPS."
            ),
            symbols=["HDFCBANK"],
        ),
        evidence,
    )

    assert result.evidence_count == 2
    assert (
        result.chunks[0].total_score
        >= result.chunks[1].total_score
    )
