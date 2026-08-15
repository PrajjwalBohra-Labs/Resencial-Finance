from typing import Protocol

from backend.app.domain.research import (
    ResearchAnswer,
    ResearchContext,
    ResearchRequest,
)
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
    ) -> None:
        self._evidence_assembler = evidence_assembler
        self._research_engine = research_engine

    async def research(
        self,
        request: ResearchRequest,
    ) -> ResearchAnswer:
        context = await self._evidence_assembler.assemble(request)

        return await self._research_engine.research(context)
