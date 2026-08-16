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
    assert len(result.evidence) == 1
    assert result.evidence[0].title == "HDFC Bank market data"
    assert result.evidence[0].symbol == "HDFCBANK"


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
from backend.app.domain.research_validation import ResearchValidationStatus
from backend.app.services.research_answer_validator import ResearchAnswerValidator


class ConflictingLLMProvider:
    provider_name = "fake_llm"

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        return LLMResponse(
            model=request.model,
            content="On 2026-08-10, the stock declined by 0.5%.",
            provider=self.provider_name,
        )


def create_validation_context() -> ResearchContext:
    return ResearchContext(
        request=ResearchRequest(
            question="Analyse HDFC Bank.",
            symbols=["HDFCBANK"],
            exchange="NSE",
            focus=ResearchFocus.MARKET,
        ),
        evidence=[
            Evidence(
                evidence_type=EvidenceType.MARKET_DATA,
                title="HDFC Bank market data",
                content=(
                    "Daily open-to-close changes:\n"
                    "2026-08-10: change=-0.5; "
                    "change_percentage=-0.0683526999316473%"
                ),
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
async def test_research_engine_attaches_passed_validation() -> None:
    provider = FakeLLMProvider()
    engine = ResearchEngine(
        llm_provider=provider,
        model="test-model",
    )

    result = await engine.research(create_context())

    assert result.validation.status == (
        ResearchValidationStatus.PASSED
    )
    assert result.validation.issues == []


@pytest.mark.asyncio
async def test_research_engine_flags_numeric_conflict() -> None:
    engine = ResearchEngine(
        llm_provider=ConflictingLLMProvider(),
        model="test-model",
        validator=ResearchAnswerValidator(),
    )

    result = await engine.research(
        create_validation_context()
    )

    assert result.validation.status == (
        ResearchValidationStatus.FAILED
    )
    assert len(result.validation.issues) == 1
    assert result.validation.issues[0].code == (
        "daily_percentage_conflict"
    )
class CorrectingLLMProvider:
    provider_name = "fake_llm"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []
        self.calls = 0

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        self.requests.append(request)
        self.calls += 1

        if self.calls == 1:
            return LLMResponse(
                model=request.model,
                content="On August 10, the stock declined by 0.5%.",
                provider=self.provider_name,
            )

        return LLMResponse(
            model=request.model,
            content="On August 10, the stock declined by 0.07%.",
            provider=self.provider_name,
        )


class AlwaysConflictingLLMProvider:
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
            content="On August 10, the stock declined by 0.5%.",
            provider=self.provider_name,
        )


@pytest.mark.asyncio
async def test_research_engine_retries_once_after_validation_failure() -> None:
    provider = CorrectingLLMProvider()

    engine = ResearchEngine(
        llm_provider=provider,
        model="test-model",
        validator=ResearchAnswerValidator(),
    )

    result = await engine.research(
        create_validation_context()
    )

    assert provider.calls == 2
    assert len(provider.requests) == 2

    assert "Validation issues:" in (
        provider.requests[1].messages[1].content
    )

    assert result.answer == (
        "On August 10, the stock declined by 0.07%."
    )

    assert result.validation.status == (
        ResearchValidationStatus.PASSED
    )


@pytest.mark.asyncio
async def test_research_engine_stops_after_one_failed_retry() -> None:
    provider = AlwaysConflictingLLMProvider()

    engine = ResearchEngine(
        llm_provider=provider,
        model="test-model",
        validator=ResearchAnswerValidator(),
    )

    result = await engine.research(
        create_validation_context()
    )

    assert len(provider.requests) == 2

    assert result.validation.status == (
        ResearchValidationStatus.FAILED
    )

    assert len(result.validation.issues) == 1

