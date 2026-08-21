from datetime import date

import pytest

from backend.app.api.routes.research import get_research_orchestrator
from backend.app.data.providers.market import MarketDataProvider
from backend.app.domain.llm import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
)
from backend.app.domain.research import ResearchAnswer
from backend.app.instruments import resolver
from backend.app.main import app
from backend.app.services.market_service import MarketService
from backend.app.services.research_data_assembler import ResearchDataAssembler
from backend.app.services.research_engine import ResearchEngine
from backend.app.services.research_orchestrator import ResearchOrchestrator
from backend.app.schemas.market import HistoricalPrice
from fastapi.testclient import TestClient


class FakeMarketProvider(MarketDataProvider):
    name = "fake-market"

    async def get_quote(self, symbol: str):
        raise NotImplementedError

    async def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        return [
            HistoricalPrice(
                date="2026-08-10",
                open=748.0,
                high=752.0,
                low=747.0,
                close=750.0,
                volume=1000000,
            ),
            HistoricalPrice(
                date="2026-08-11",
                open=750.0,
                high=757.0,
                low=749.0,
                close=755.0,
                volume=1200000,
            ),
        ]

    async def get_equity(self, symbol: str):
        raise NotImplementedError


class FakeLLMProvider(LLMProvider):
    @property
    def provider_name(self) -> str:
        return "fake-llm"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        assert request.model == "integration-test-model"
        assert len(request.messages) == 2

        user_prompt = request.messages[1].content

        assert "Analyse HDFC Bank." in user_prompt
        assert "750.0" in user_prompt
        assert "755.0" in user_prompt

        return LLMResponse(
            model="integration-test-model",
            content="Integrated research completed from supplied market evidence.",
            provider=self.provider_name,
        )


def build_integration_orchestrator() -> ResearchOrchestrator:
    market_service = MarketService(
        provider=FakeMarketProvider(),
        resolver=resolver,
    )

    assembler = ResearchDataAssembler(
        market_service=market_service,
    )

    engine = ResearchEngine(
        llm_provider=FakeLLMProvider(),
        model="integration-test-model",
    )

    return ResearchOrchestrator(
        evidence_assembler=assembler,
        research_engine=engine,
    )


def test_research_endpoint_integrates_evidence_and_llm() -> None:
    orchestrator = build_integration_orchestrator()

    app.dependency_overrides[get_research_orchestrator] = (
        lambda: orchestrator
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/api/research",
            json={
                "question": "Analyse HDFC Bank.",
                "symbols": ["HDFCBANK"],
                "exchange": "NSE",
                "focus": "market",
                "start_date": "2026-08-10",
                "end_date": "2026-08-11",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["question"] == "Analyse HDFC Bank."
        assert body["answer"] == (
            "Integrated research completed from supplied market evidence."
        )
        assert body["model"] == "integration-test-model"
        assert body["provider"] == "fake-llm"
        assert body["evidence_count"] == 2

    finally:
        app.dependency_overrides.clear()
