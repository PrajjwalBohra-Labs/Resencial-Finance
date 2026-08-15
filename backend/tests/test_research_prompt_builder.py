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
