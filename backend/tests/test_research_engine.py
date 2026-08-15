from datetime import datetime, timezone

import pytest

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)
from backend.app.domain.llm import LLMRequest, LLMResponse
from backend.app.domain.research import (
    ResearchContext,
    ResearchFocus,
    ResearchRequest,
)
from backend.app.services.research_engine import ResearchEngine


class FakeLLMProvider:
    provider_name = "fake_llm"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        self.requests.append(request)

        return LLMResponse(
            model=request.model,
            content="HDFC Bank research response.",
            provider=self.provider_name,
        )


def create_context() -> ResearchContext:
    return ResearchContext(
        request=ResearchRequest(
            question="Analyse HDFC Bank's recent performance.",
            symbols=["HDFCBANK"],
            exchange="NSE",
            focus=ResearchFocus.MARKET,
        ),
        evidence=[
            Evidence(
                evidence_type=EvidenceType.MARKET_DATA,
                title="HDFC Bank market data",
                content="Close price increased from 750 to 755.",
                source=EvidenceSource(
                    name="Yahoo Finance",
                    provider="yahoo_finance",
                    retrieved_at=datetime.now(timezone.utc),
                ),
                symbol="HDFCBANK",
                exchange="NSE",
            )
        ],
    )


@pytest.mark.asyncio
async def test_research_engine_returns_answer() -> None:
    provider = FakeLLMProvider()
    engine = ResearchEngine(
        llm_provider=provider,
        model="test-model",
    )

    result = await engine.research(create_context())

    assert result.question == (
        "Analyse HDFC Bank's recent performance."
    )
    assert result.answer == "HDFC Bank research response."
    assert result.model == "test-model"
    assert result.provider == "fake_llm"
    assert result.evidence_count == 1


@pytest.mark.asyncio
async def test_research_engine_sends_system_and_user_messages() -> None:
    provider = FakeLLMProvider()
    engine = ResearchEngine(
        llm_provider=provider,
        model="test-model",
    )

    await engine.research(create_context())

    assert len(provider.requests) == 1

    request = provider.requests[0]

    assert request.model == "test-model"
    assert len(request.messages) == 2

    assert request.messages[0].role.value == "system"
    assert request.messages[1].role.value == "user"

    assert "Resencial Finance" in request.messages[0].content
    assert "HDFC Bank" in request.messages[1].content
    assert "HDFC Bank market data" in request.messages[1].content


@pytest.mark.asyncio
async def test_research_engine_uses_configured_temperature() -> None:
    provider = FakeLLMProvider()

    engine = ResearchEngine(
        llm_provider=provider,
        model="test-model",
        temperature=0.4,
    )

    await engine.research(create_context())

    assert provider.requests[0].temperature == 0.4


@pytest.mark.asyncio
async def test_research_engine_supports_empty_evidence() -> None:
    provider = FakeLLMProvider()
    engine = ResearchEngine(
        llm_provider=provider,
        model="test-model",
    )

    context = ResearchContext(
        request=ResearchRequest(
            question="Research HDFC Bank.",
            symbols=["HDFCBANK"],
        )
    )

    result = await engine.research(context)

    assert result.answer == "HDFC Bank research response."
    assert result.evidence_count == 0

    request = provider.requests[0]

    assert "No research evidence is currently available." in (
        request.messages[1].content
    )


@pytest.mark.asyncio
async def test_research_engine_preserves_provider_identity() -> None:
    provider = FakeLLMProvider()
    engine = ResearchEngine(
        llm_provider=provider,
        model="research-model",
    )

    result = await engine.research(create_context())

    assert result.provider == "fake_llm"
    assert result.model == "research-model"
