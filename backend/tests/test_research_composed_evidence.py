from datetime import date, datetime, timezone

import pytest

from backend.app.data.evidence.bond_evidence_adapter import BondEvidenceAdapter
from backend.app.data.evidence.filing_evidence_adapter import FilingEvidenceAdapter
from backend.app.data.evidence.macro_evidence_adapter import MacroEvidenceAdapter
from backend.app.data.evidence.news_evidence_adapter import NewsEvidenceAdapter
from backend.app.data.providers.in_memory_research import InMemoryResearchProvider
from backend.app.domain.evidence import EvidenceType
from backend.app.domain.research import ResearchFocus, ResearchRequest
from backend.app.domain.research_sources import (
    BondRecord,
    BondYieldRecord,
    FilingRecord,
    MacroObservation,
    NewsRecord,
)
from backend.app.services.research_data_assembler import ResearchDataAssembler


def build_provider() -> InMemoryResearchProvider:
    now = datetime.now(timezone.utc)

    return InMemoryResearchProvider(
        news=[
            NewsRecord(
                title="Test company news",
                source_name="test-news",
                retrieved_at=now,
                provider="test",
                symbol="RELIANCE",
                summary="Deterministic news evidence.",
            ),
        ],
        filings=[
            FilingRecord(
                title="Test annual filing",
                source_name="test-filings",
                retrieved_at=now,
                provider="test",
                symbol="RELIANCE",
                filing_type="annual",
                filing_date=date(2026, 3, 31),
            ),
        ],
        macro=[
            MacroObservation(
                series_name="repo rate",
                observation_date=date(2026, 8, 21),
                value=6.5,
                unit="percent",
                source_name="test-macro",
                retrieved_at=now,
                provider="test",
            ),
        ],
        bonds=[
            BondRecord(
                title="Test government bond",
                source_name="test-bonds",
                retrieved_at=now,
                provider="test",
                identifier="GSEC-TEST",
                issuer="Government of India",
            ),
        ],
        bond_yields=[
            BondYieldRecord(
                identifier="GSEC-TEST",
                yield_value=6.8,
                observation_date=date(2026, 8, 21),
                source_name="test-bonds",
                retrieved_at=now,
                provider="test",
            ),
        ],
    )


def build_assembler() -> ResearchDataAssembler:
    provider = build_provider()

    return ResearchDataAssembler(
        market_service=None,  # type: ignore[arg-type]
        fundamentals_service=None,
        news_evidence_port=NewsEvidenceAdapter(provider),
        filing_evidence_port=FilingEvidenceAdapter(provider),
        macro_evidence_port=MacroEvidenceAdapter(provider),
        bond_evidence_port=BondEvidenceAdapter(provider),
    )


@pytest.mark.asyncio
async def test_general_focus_collects_general_research_evidence() -> None:
    assembler = build_assembler()

    request = ResearchRequest(
        question="repo rate",
        symbols=["RELIANCE"],
        exchange="NSE",
        focus=ResearchFocus.GENERAL,
    )

    context = await assembler.assemble(request)

    assert len(context.evidence) == 3

    evidence_types = {
        item.evidence_type
        for item in context.evidence
    }

    assert evidence_types == {
        EvidenceType.NEWS,
        EvidenceType.FILING,
        EvidenceType.MACRO,
    }


@pytest.mark.asyncio
async def test_fixed_income_focus_collects_bond_evidence() -> None:
    assembler = build_assembler()

    request = ResearchRequest(
        question="GSEC-TEST",
        focus=ResearchFocus.FIXED_INCOME,
    )

    context = await assembler.assemble(request)

    assert len(context.evidence) == 2

    titles = {item.title for item in context.evidence}

    assert "Test government bond" in titles
    assert "GSEC-TEST bond yield" in titles


@pytest.mark.asyncio
async def test_macro_focus_excludes_unrelated_advanced_evidence() -> None:
    assembler = build_assembler()

    request = ResearchRequest(
        question="repo rate",
        focus=ResearchFocus.MACRO,
    )

    context = await assembler.assemble(request)

    assert len(context.evidence) == 1
    assert context.evidence[0].evidence_type == EvidenceType.MACRO
    assert context.evidence[0].title == "repo rate"


@pytest.mark.asyncio
async def test_fixed_income_focus_does_not_collect_macro_or_news() -> None:
    assembler = build_assembler()

    request = ResearchRequest(
        question="GSEC-TEST",
        focus=ResearchFocus.FIXED_INCOME,
    )

    context = await assembler.assemble(request)

    evidence_types = {
        item.evidence_type
        for item in context.evidence
    }

    assert EvidenceType.NEWS not in evidence_types
    assert EvidenceType.FILING not in evidence_types
    assert EvidenceType.MACRO not in evidence_types
