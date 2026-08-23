from datetime import datetime, timezone

import pytest

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)
from backend.app.retrieval.models import RetrievalQuery
from backend.app.retrieval.research_context_builder import (
    ResearchContextBuilder,
)
from backend.app.retrieval.retriever import EvidenceRetriever


def make_evidence(
    *,
    content: str,
    symbol: str = "HDFCBANK",
) -> Evidence:
    return Evidence(
        evidence_type=EvidenceType.FUNDAMENTAL,
        title=f"{symbol} fundamentals",
        content=content,
        source=EvidenceSource(
            name="Test Provider",
            provider="test_provider",
            retrieved_at=datetime(
                2026,
                8,
                19,
                tzinfo=timezone.utc,
            ),
        ),
        symbol=symbol,
        exchange="NSE",
        confidence=1.0,
    )


@pytest.mark.asyncio
async def test_context_builder_returns_ranked_context() -> None:
    builder = ResearchContextBuilder(
        EvidenceRetriever()
    )

    evidence = [
        make_evidence(
            content=(
                "HDFCBANK revenue increased by 20%."
            ),
        ),
        make_evidence(
            content=(
                "HDFCBANK ROE was 15%."
            ),
        ),
    ]

    query = RetrievalQuery(
        question="Analyse HDFCBANK revenue growth.",
        symbols=["HDFCBANK"],
    )

    context = await builder.build(
        query,
        evidence,
    )

    assert context.request.question == query.question
    assert context.request.symbols == ["HDFCBANK"]
    assert context.request.exchange is None

    assert len(context.evidence) >= 1
    assert all(
        item.symbol == "HDFCBANK"
        for item in context.evidence
    )


@pytest.mark.asyncio
async def test_context_builder_preserves_retrieval_order() -> None:
    builder = ResearchContextBuilder(
        EvidenceRetriever()
    )

    evidence = [
        make_evidence(
            content="HDFCBANK revenue.",
        ),
        make_evidence(
            content=(
                "HDFCBANK revenue growth, earnings growth, "
                "profitability and EPS analysis."
            ),
        ),
    ]

    query = RetrievalQuery(
        question=(
            "Analyse HDFCBANK revenue growth "
            "earnings profitability and EPS."
        ),
        symbols=["HDFCBANK"],
    )

    context = await builder.build(
        query,
        evidence,
    )

    assert len(context.evidence) == 2
    assert (
        "revenue growth, earnings growth"
        in context.evidence[0].content
    )


@pytest.mark.asyncio
async def test_context_builder_deduplicates_evidence() -> None:
    builder = ResearchContextBuilder(
        EvidenceRetriever()
    )

    item = make_evidence(
        content="HDFCBANK revenue growth was 20%.",
    )

    query = RetrievalQuery(
        question="Analyse HDFCBANK revenue growth.",
        symbols=["HDFCBANK"],
    )

    context = await builder.build(
        query,
        [item, item],
    )

    assert len(context.evidence) == 1


@pytest.mark.asyncio
async def test_context_builder_applies_character_budget() -> None:
    builder = ResearchContextBuilder(
        EvidenceRetriever(),
        max_chars=300,
    )

    evidence = [
        make_evidence(
            content="A" * 200,
        ),
        make_evidence(
            content="B" * 200,
            symbol="ICICIBANK",
        ),
    ]

    query = RetrievalQuery(
        question="Analyse bank fundamentals.",
        symbols=["HDFCBANK", "ICICIBANK"],
    )

    context = await builder.build(
        query,
        evidence,
    )

    rendered = "\n\n".join(
        item.content
        for item in context.evidence
    )

    assert len(rendered) <= 400
    assert len(context.evidence) <= 2


@pytest.mark.asyncio
async def test_context_builder_returns_empty_context_without_evidence() -> None:
    builder = ResearchContextBuilder(
        EvidenceRetriever()
    )

    query = RetrievalQuery(
        question="Analyse HDFCBANK.",
        symbols=["HDFCBANK"],
    )

    context = await builder.build(
        query,
        [],
    )

    assert context.request.question == "Analyse HDFCBANK."
    assert context.evidence == []


@pytest.mark.asyncio
async def test_context_builder_preserves_contextual_evidence() -> None:
    builder = ResearchContextBuilder(EvidenceRetriever())

    primary = make_evidence(
        content="HDFCBANK revenue increased by 20%.",
        symbol="HDFCBANK",
    )

    benchmark = Evidence(
        evidence_type=EvidenceType.MARKET_DATA,
        title="NIFTY 50 benchmark",
        content="NIFTY 50 closed at 24800.",
        source=EvidenceSource(
            name="Benchmark Provider",
            provider="test_provider",
            retrieved_at=datetime(
                2026,
                8,
                19,
                tzinfo=timezone.utc,
            ),
        ),
        symbol="^NSEI",
        exchange="NSE",
        confidence=1.0,
    )

    query = RetrievalQuery(
        question="Analyse HDFCBANK.",
        symbols=["HDFCBANK"],
        exchange="NSE",
    )

    context = await builder.build(
        query,
        [primary, benchmark],
        contextual_evidence=[benchmark],
    )

    assert len(context.evidence) == 2
    assert context.evidence[0].symbol == "HDFCBANK"
    assert context.evidence[1].symbol == "^NSEI"
