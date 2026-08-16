from fastapi import APIRouter, Depends, HTTPException

from backend.app.core.config import get_settings
from backend.app.core.exceptions import (
    LLMProviderError,
    MarketDataProviderError,
)
from backend.app.data.providers import (
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

    evidence_assembler = ResearchDataAssembler(
        market_service=market_service,
        fundamentals_service=fundamentals_service,
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

    except MarketDataProviderError as exc:
        raise HTTPException(
            status_code=503,
            detail="Market data provider is temporarily unavailable.",
        ) from exc

    except LLMProviderError as exc:
        raise HTTPException(
            status_code=503,
            detail="Research model provider is temporarily unavailable.",
        ) from exc

