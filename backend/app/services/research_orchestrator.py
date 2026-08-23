from typing import Protocol

from backend.app.domain.research import (
    ResearchAnswer,
    ResearchContext,
    ResearchRequest,
)
from backend.app.retrieval.models import RetrievalQuery
from backend.app.retrieval.research_context_builder import ResearchContextBuilder
from backend.app.retrieval.retriever import EvidenceRetriever
from backend.app.services.research_engine import ResearchEngine


class ResearchEvidenceAssembler(Protocol):
    """Builds research context from available evidence sources."""

    async def assemble(
        self,
        request: ResearchRequest,
    ) -> ResearchContext:
        ...


class ResearchOrchestrator:
    """Coordinates evidence assembly and research generation."""

    def __init__(
        self,
        *,
        evidence_assembler: ResearchEvidenceAssembler,
        research_engine: ResearchEngine,
        context_builder: ResearchContextBuilder | None = None,
    ) -> None:
        self._evidence_assembler = evidence_assembler
        self._research_engine = research_engine
        self._context_builder = (
            context_builder
            or ResearchContextBuilder(EvidenceRetriever())
        )

    async def research(
        self,
        request: ResearchRequest,
    ) -> ResearchAnswer:
        assembled_context = await self._evidence_assembler.assemble(
            request
        )

        retrieval_query = RetrievalQuery(
            question=request.question,
            symbols=request.symbols,
            exchange=request.exchange,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        context = await self._context_builder.build(
            retrieval_query,
            assembled_context.evidence,
            contextual_evidence=assembled_context.evidence,
        )

        context = context.model_copy(
            update={
                "request": request,
                "analytical_findings": (
                    assembled_context.analytical_findings
                ),
            }
        )

        return await self._research_engine.research(context)
