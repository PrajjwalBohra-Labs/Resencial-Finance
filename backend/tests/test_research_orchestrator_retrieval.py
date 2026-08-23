import pytest

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)
from backend.app.domain.research import (
    ResearchAnswer,
    ResearchContext,
    ResearchFocus,
    ResearchRequest,
)
from backend.app.retrieval.research_context_builder import (
    ResearchContextBuilder,
)
from backend.app.retrieval.retriever import EvidenceRetriever
from backend.app.services.research_orchestrator import (
    ResearchOrchestrator,
)


def make_evidence(
    *,
    title: str,
    content: str,
    symbol: str = "HDFCBANK",
) -> Evidence:
    from datetime import datetime, timezone

    return Evidence(
        evidence_type=EvidenceType.FUNDAMENTAL,
        title=title,
        content=content,
        source=EvidenceSource(
            name="test",
            provider="test",
            retrieved_at=datetime.now(timezone.utc),
        ),
        symbol=symbol,
        exchange="NSE",
    )


class FakeAssembler:
    def __init__(self, context: ResearchContext) -> None:
        self.context = context

    async def assemble(
        self,
        request: ResearchRequest,
    ) -> ResearchContext:
        return self.context


class FakeEngine:
    def __init__(self) -> None:
        self.contexts: list[ResearchContext] = []

    async def research(
        self,
        context: ResearchContext,
    ) -> ResearchAnswer:
        self.contexts.append(context)

        return ResearchAnswer(
            question=context.request.question,
            answer="ok",
            model="test",
            provider="test",
            evidence_count=len(context.evidence),
            evidence=context.evidence,
            analytical_findings=context.analytical_findings,
        )


def make_request() -> ResearchRequest:
    return ResearchRequest(
        question="Analyse HDFCBANK revenue growth",
        symbols=["HDFCBANK"],
        exchange="NSE",
        focus=ResearchFocus.FUNDAMENTAL,
    )


@pytest.mark.asyncio
async def test_orchestrator_retrieves_assembled_evidence() -> None:
    request = make_request()

    evidence = [
        make_evidence(
            title="Revenue",
            content="HDFCBANK revenue growth was 20%.",
        ),
        make_evidence(
            title="ROE",
            content="HDFCBANK ROE was 15%.",
        ),
    ]

    assembled = ResearchContext(
        request=request,
        evidence=evidence,
    )

    engine = FakeEngine()

    orchestrator = ResearchOrchestrator(
        evidence_assembler=FakeAssembler(assembled),
        research_engine=engine,
        context_builder=ResearchContextBuilder(EvidenceRetriever()),
    )

    await orchestrator.research(request)

    assert len(engine.contexts) == 1
    context = engine.contexts[0]

    assert context.request == request
    assert len(context.evidence) >= 1
    assert all(
        item.symbol == "HDFCBANK"
        for item in context.evidence
    )


@pytest.mark.asyncio
async def test_orchestrator_preserves_analytical_findings() -> None:
    request = make_request()

    assembled = ResearchContext(
        request=request,
        evidence=[
            make_evidence(
                title="Revenue",
                content="HDFCBANK revenue growth was 20%.",
            ),
        ],
    )

    engine = FakeEngine()

    orchestrator = ResearchOrchestrator(
        evidence_assembler=FakeAssembler(assembled),
        research_engine=engine,
    )

    await orchestrator.research(request)

    assert engine.contexts[0].analytical_findings == (
        assembled.analytical_findings
    )


@pytest.mark.asyncio
async def test_orchestrator_returns_engine_result() -> None:
    request = make_request()

    assembled = ResearchContext(
        request=request,
        evidence=[],
    )

    engine = FakeEngine()

    orchestrator = ResearchOrchestrator(
        evidence_assembler=FakeAssembler(assembled),
        research_engine=engine,
    )

    result = await orchestrator.research(request)

    assert result.question == request.question
    assert result.answer == "ok"
