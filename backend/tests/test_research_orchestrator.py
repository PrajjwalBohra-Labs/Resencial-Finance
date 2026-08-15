import pytest

from backend.app.domain.research import (
    ResearchAnswer,
    ResearchContext,
    ResearchFocus,
    ResearchRequest,
)
from backend.app.services.research_orchestrator import (
    ResearchOrchestrator,
)


class FakeEvidenceAssembler:
    def __init__(self) -> None:
        self.requests: list[ResearchRequest] = []

    async def assemble(
        self,
        request: ResearchRequest,
    ) -> ResearchContext:
        self.requests.append(request)

        return ResearchContext(
            request=request,
        )


class FakeResearchEngine:
    def __init__(self) -> None:
        self.contexts: list[ResearchContext] = []

    async def research(
        self,
        context: ResearchContext,
    ) -> ResearchAnswer:
        self.contexts.append(context)

        return ResearchAnswer(
            question=context.request.question,
            answer="Research completed.",
            model="test-model",
            provider="fake_llm",
            evidence_count=len(context.evidence),
        )


def create_request() -> ResearchRequest:
    return ResearchRequest(
        question="Analyse HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        focus=ResearchFocus.FUNDAMENTAL,
    )


@pytest.mark.asyncio
async def test_orchestrator_assembles_context_before_research() -> None:
    assembler = FakeEvidenceAssembler()
    engine = FakeResearchEngine()

    orchestrator = ResearchOrchestrator(
        evidence_assembler=assembler,
        research_engine=engine,
    )

    request = create_request()

    result = await orchestrator.research(request)

    assert result.question == "Analyse HDFC Bank."
    assert result.answer == "Research completed."

    assert assembler.requests == [request]

    assert len(engine.contexts) == 1
    assert engine.contexts[0].request == request


@pytest.mark.asyncio
async def test_orchestrator_passes_assembled_context_to_engine() -> None:
    assembler = FakeEvidenceAssembler()
    engine = FakeResearchEngine()

    orchestrator = ResearchOrchestrator(
        evidence_assembler=assembler,
        research_engine=engine,
    )

    request = create_request()

    await orchestrator.research(request)

    context = engine.contexts[0]

    assert context.request.question == request.question
    assert context.request.symbols == ["HDFCBANK"]
    assert context.request.exchange == "NSE"
    assert context.request.focus == ResearchFocus.FUNDAMENTAL


@pytest.mark.asyncio
async def test_orchestrator_returns_engine_result_unchanged() -> None:
    assembler = FakeEvidenceAssembler()
    engine = FakeResearchEngine()

    orchestrator = ResearchOrchestrator(
        evidence_assembler=assembler,
        research_engine=engine,
    )

    result = await orchestrator.research(create_request())

    assert isinstance(result, ResearchAnswer)
    assert result.model == "test-model"
    assert result.provider == "fake_llm"
    assert result.evidence_count == 0


@pytest.mark.asyncio
async def test_orchestrator_supports_multiple_symbols() -> None:
    assembler = FakeEvidenceAssembler()
    engine = FakeResearchEngine()

    orchestrator = ResearchOrchestrator(
        evidence_assembler=assembler,
        research_engine=engine,
    )

    request = ResearchRequest(
        question="Compare HDFC Bank and ICICI Bank.",
        symbols=["HDFCBANK", "ICICIBANK"],
        exchange="NSE",
        focus=ResearchFocus.COMPARISON,
    )

    result = await orchestrator.research(request)

    assert result.question == (
        "Compare HDFC Bank and ICICI Bank."
    )

    assert engine.contexts[0].request.symbols == [
        "HDFCBANK",
        "ICICIBANK",
    ]


@pytest.mark.asyncio
async def test_orchestrator_does_not_generate_research_without_assembly() -> None:
    assembler = FakeEvidenceAssembler()
    engine = FakeResearchEngine()

    orchestrator = ResearchOrchestrator(
        evidence_assembler=assembler,
        research_engine=engine,
    )

    request = create_request()

    await orchestrator.research(request)

    assert len(assembler.requests) == 1
    assert len(engine.contexts) == 1
