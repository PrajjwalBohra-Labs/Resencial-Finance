from datetime import datetime, timezone

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)
from backend.app.domain.research import ResearchContext, ResearchFocus, ResearchRequest
from backend.app.services.research_prompt_builder import ResearchPromptBuilder


def create_context() -> ResearchContext:
    request = ResearchRequest(
        question="Analyse HDFC Bank's recent market performance.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        focus=ResearchFocus.MARKET,
    )

    evidence = Evidence(
        evidence_type=EvidenceType.MARKET_DATA,
        title="HDFC Bank market history",
        content=(
            "2026-08-10 close=750.0 volume=1000000\n"
            "2026-08-11 close=755.0 volume=1200000"
        ),
        source=EvidenceSource(
            name="Yahoo Finance",
            provider="yahoo_finance",
            retrieved_at=datetime(
                2026,
                8,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        ),
        symbol="HDFCBANK",
        exchange="NSE",
        confidence=1.0,
    )

    return ResearchContext(
        request=request,
        evidence=[evidence],
    )


def test_prompt_builder_returns_system_and_user_prompts() -> None:
    builder = ResearchPromptBuilder()

    system_prompt, user_prompt = builder.build(create_context())

    assert system_prompt
    assert user_prompt


def test_system_prompt_defines_research_boundaries() -> None:
    builder = ResearchPromptBuilder()

    system_prompt, _ = builder.build(create_context())

    assert "Resencial Finance" in system_prompt
    assert "Do not invent financial facts" in system_prompt
    assert "Do not provide buy, sell, entry, exit, or trading instructions" in system_prompt
    assert "Indian financial context" in system_prompt


def test_user_prompt_contains_research_question() -> None:
    builder = ResearchPromptBuilder()

    _, user_prompt = builder.build(create_context())

    assert "Analyse HDFC Bank's recent market performance." in user_prompt
    assert "HDFCBANK" in user_prompt
    assert "NSE" in user_prompt


def test_user_prompt_contains_evidence() -> None:
    builder = ResearchPromptBuilder()

    _, user_prompt = builder.build(create_context())

    assert "HDFC Bank market history" in user_prompt
    assert "Yahoo Finance" in user_prompt
    assert "2026-08-10 close=750.0 volume=1000000" in user_prompt
    assert "2026-08-11 close=755.0 volume=1200000" in user_prompt


def test_prompt_builder_handles_empty_evidence() -> None:
    context = ResearchContext(
        request=ResearchRequest(
            question="Research HDFC Bank.",
            symbols=["HDFCBANK"],
        )
    )

    builder = ResearchPromptBuilder()

    _, user_prompt = builder.build(context)

    assert "No research evidence is currently available." in user_prompt


def test_prompt_builder_includes_source_url_when_available() -> None:
    context = create_context()

    context.evidence[0].source.url = "https://example.com/source"

    builder = ResearchPromptBuilder()

    _, user_prompt = builder.build(context)

    assert "https://example.com/source" in user_prompt


def test_prompt_builder_includes_mixed_evidence_sources() -> None:
    from datetime import datetime, timezone

    from backend.app.domain.evidence import (
        Evidence,
        EvidenceSource,
        EvidenceType,
    )
    from backend.app.domain.research import (
        ResearchContext,
        ResearchRequest,
    )

    now = datetime.now(timezone.utc)

    def source(name: str, provider: str) -> EvidenceSource:
        return EvidenceSource(
            name=name,
            provider=provider,
            retrieved_at=now,
        )

    context = ResearchContext(
        request=ResearchRequest(
            question="Assess HDFC Bank using all available evidence.",
            symbols=["HDFCBANK"],
            exchange="NSE",
        ),
        evidence=[
            Evidence(
                evidence_type=EvidenceType.MARKET_DATA,
                title="HDFC Bank market history",
                content="HDFCBANK closed at 755 on 2026-08-11.",
                source=source("Yahoo Finance", "yahoo_finance"),
                symbol="HDFCBANK",
                exchange="NSE",
            ),
            Evidence(
                evidence_type=EvidenceType.NEWS,
                title="HDFC Bank news",
                content="The supplied news record contains company commentary.",
                source=source("Test News", "test-news"),
                symbol="HDFCBANK",
                exchange="NSE",
            ),
            Evidence(
                evidence_type=EvidenceType.FILING,
                title="HDFC Bank annual filing",
                content="The supplied filing contains regulatory disclosures.",
                source=source("Test Filing", "test-filings"),
                symbol="HDFCBANK",
                exchange="NSE",
            ),
            Evidence(
                evidence_type=EvidenceType.MACRO,
                title="Repo rate",
                content="Repo rate observation: 6.5 percent.",
                source=source("Test Macro", "test-macro"),
            ),
            Evidence(
                evidence_type=EvidenceType.REGULATORY,
                title="Government bond",
                content="Government bond yield: 6.8%.",
                source=source("Test Bonds", "test-bonds"),
            ),
        ],
    )

    system_prompt, user_prompt = ResearchPromptBuilder().build(context)

    assert "type=market_data" in user_prompt
    assert "type=news" in user_prompt
    assert "type=filing" in user_prompt
    assert "type=macro" in user_prompt
    assert "type=regulatory" in user_prompt

    assert "HDFC Bank market history" in user_prompt
    assert "HDFC Bank news" in user_prompt
    assert "HDFC Bank annual filing" in user_prompt
    assert "Repo rate" in user_prompt
    assert "Government bond" in user_prompt

    assert "source_name=Yahoo Finance" in user_prompt
    assert "provider=test-news" in user_prompt
    assert "provider=test-filings" in user_prompt
    assert "provider=test-macro" in user_prompt
    assert "provider=test-bonds" in user_prompt

    assert "You are Resencial Finance" in system_prompt
