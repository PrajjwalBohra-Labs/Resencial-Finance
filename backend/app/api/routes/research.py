from fastapi import APIRouter, Depends, HTTPException

from backend.app.core.config import get_settings
from backend.app.core.exceptions import (
    DataProviderError,
    LLMProviderError,
    MarketDataProviderError,
)
from backend.app.data.evidence.bond_evidence_adapter import (
    BondEvidenceAdapter,
)
from backend.app.data.evidence.filing_evidence_adapter import (
    FilingEvidenceAdapter,
)
from backend.app.data.evidence.macro_evidence_adapter import (
    MacroEvidenceAdapter,
)
from backend.app.data.evidence.news_evidence_adapter import (
    NewsEvidenceAdapter,
)
from backend.app.data.providers import (
    InMemoryResearchProvider,
    YahooFinanceFundamentalsProvider,
    YahooFinanceMarketProvider,
)
from backend.app.domain.research import ResearchAnswer, ResearchRequest
from backend.app.instruments import InstrumentResolutionError, resolver
from backend.app.llm.ollama import OllamaProvider
from backend.app.services.fundamentals_service import FundamentalsService
from backend.app.services.market_service import MarketService
from backend.app.services.research_data_assembler import ResearchDataAssembler
from backend.app.services.research_engine import ResearchEngine
from backend.app.services.research_orchestrator import ResearchOrchestrator

router = APIRouter(prefix="/research", tags=["research"])


def get_research_orchestrator() -> ResearchOrchestrator:
    settings = get_settings()

    market_service = MarketService(
        provider=YahooFinanceMarketProvider(),
        resolver=resolver,
    )

    fundamentals_service = FundamentalsService(
        provider=YahooFinanceFundamentalsProvider(),
    )

    research_provider = InMemoryResearchProvider()

    news_evidence_port = NewsEvidenceAdapter(
        provider=research_provider,
    )

    filing_evidence_port = FilingEvidenceAdapter(
        provider=research_provider,
    )

    macro_evidence_port = MacroEvidenceAdapter(
        provider=research_provider,
    )

    bond_evidence_port = BondEvidenceAdapter(
        provider=research_provider,
    )

    evidence_assembler = ResearchDataAssembler(
        market_service=market_service,
        fundamentals_service=fundamentals_service,
        news_evidence_port=news_evidence_port,
        filing_evidence_port=filing_evidence_port,
        macro_evidence_port=macro_evidence_port,
        bond_evidence_port=bond_evidence_port,
    )

    llm_provider = OllamaProvider(
        base_url=settings.ollama_base_url,
    )

    research_engine = ResearchEngine(
        llm_provider=llm_provider,
        model=settings.ollama_model or "llama3.2",
    )

    return ResearchOrchestrator(
        evidence_assembler=evidence_assembler,
        research_engine=research_engine,
    )


@router.post("", response_model=ResearchAnswer)
async def research(
    request: ResearchRequest,
    orchestrator: ResearchOrchestrator = Depends(
        get_research_orchestrator,
    ),
) -> ResearchAnswer:
    try:
        return await orchestrator.research(request)

    except InstrumentResolutionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except DataProviderError as exc:
        raise HTTPException(
            status_code=503,
            detail="Market data provider is temporarily unavailable.",
        ) from exc

    except LLMProviderError as exc:
        raise HTTPException(
            status_code=503,
            detail="Research model provider is temporarily unavailable.",
        ) from exc




