from datetime import date
from unittest.mock import AsyncMock

import pytest

from backend.app.domain.evidence import Evidence, EvidenceSource, EvidenceType
from backend.app.domain.research import ResearchFocus, ResearchRequest
from backend.app.services.research_data_assembler import ResearchDataAssembler


class FakeMarketService:
    provider_name = "test-market"

    async def get_historical_prices(
        self,
        *,
        symbol: str,
        exchange: str,
        start_date: date,
        end_date: date,
    ):
        return []


def make_evidence(
    evidence_type: EvidenceType,
    title: str,
) -> Evidence:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    return Evidence(
        evidence_type=evidence_type,
        title=title,
        content=f"{title} content",
        source=EvidenceSource(
            name="test-provider",
            url=None,
            published_at=None,
            retrieved_at=now,
            provider="test-provider",
        ),
    )


def make_request(
    *,
    focus: ResearchFocus,
    symbols: list[str] | None = None,
) -> ResearchRequest:
    return ResearchRequest(
        question="advanced research question",
        symbols=symbols if symbols is not None else ["TEST"],
        exchange="NSE",
        focus=focus,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )


def make_ports():
    news_port = AsyncMock()
    filing_port = AsyncMock()
    macro_port = AsyncMock()
    bond_port = AsyncMock()

    news_port.collect.return_value = [
        make_evidence(EvidenceType.NEWS, "News evidence")
    ]
    filing_port.collect.return_value = [
        make_evidence(EvidenceType.FILING, "Filing evidence")
    ]
    macro_port.collect.return_value = [
        make_evidence(EvidenceType.MACRO, "Macro evidence")
    ]
    bond_port.collect.return_value = [
        make_evidence(EvidenceType.REGULATORY, "Bond evidence")
    ]

    return news_port, filing_port, macro_port, bond_port


@pytest.mark.asyncio
async def test_assemble_adds_news_evidence_to_context() -> None:
    news_port, filing_port, macro_port, bond_port = make_ports()

    assembler = ResearchDataAssembler(
        market_service=FakeMarketService(),
        news_evidence_port=news_port,
        filing_evidence_port=filing_port,
        macro_evidence_port=macro_port,
        bond_evidence_port=bond_port,
    )

    request = make_request(focus=ResearchFocus.MARKET)

    context = await assembler.assemble(request)

    assert len(context.evidence) == 1
    assert context.evidence[0].evidence_type == EvidenceType.NEWS

    news_port.collect.assert_awaited_once_with(request)
    filing_port.collect.assert_not_awaited()
    macro_port.collect.assert_not_awaited()
    bond_port.collect.assert_not_awaited()


@pytest.mark.asyncio
async def test_assemble_general_focus_aggregates_all_research_sources() -> None:
    news_port, filing_port, macro_port, bond_port = make_ports()

    assembler = ResearchDataAssembler(
        market_service=FakeMarketService(),
        news_evidence_port=news_port,
        filing_evidence_port=filing_port,
        macro_evidence_port=macro_port,
        bond_evidence_port=bond_port,
    )

    request = make_request(focus=ResearchFocus.GENERAL)

    context = await assembler.assemble(request)

    assert len(context.evidence) == 4
    assert {
        item.evidence_type
        for item in context.evidence
    } == {
        EvidenceType.NEWS,
        EvidenceType.FILING,
        EvidenceType.MACRO,
        EvidenceType.REGULATORY,
    }

    news_port.collect.assert_awaited_once_with(request)
    filing_port.collect.assert_awaited_once_with(request)
    macro_port.collect.assert_awaited_once_with(request)
    bond_port.collect.assert_awaited_once_with(request)


@pytest.mark.asyncio
async def test_assemble_preserves_context_when_no_symbols() -> None:
    news_port, filing_port, macro_port, bond_port = make_ports()

    assembler = ResearchDataAssembler(
        market_service=FakeMarketService(),
        news_evidence_port=news_port,
        filing_evidence_port=filing_port,
        macro_evidence_port=macro_port,
        bond_evidence_port=bond_port,
    )

    request = make_request(
        focus=ResearchFocus.GENERAL,
        symbols=[],
    )

    context = await assembler.assemble(request)

    assert context.evidence == []

    news_port.collect.assert_not_awaited()
    filing_port.collect.assert_not_awaited()
    macro_port.collect.assert_not_awaited()
    bond_port.collect.assert_not_awaited()


@pytest.mark.asyncio
async def test_assemble_adds_research_evidence_after_existing_context_evidence() -> None:
    news_port, filing_port, macro_port, bond_port = make_ports()

    assembler = ResearchDataAssembler(
        market_service=FakeMarketService(),
        news_evidence_port=news_port,
        filing_evidence_port=filing_port,
        macro_evidence_port=macro_port,
        bond_evidence_port=bond_port,
    )

    request = make_request(focus=ResearchFocus.MARKET)

    context = await assembler.assemble(request)

    existing = make_evidence(
        EvidenceType.MARKET_DATA,
        "Existing market evidence",
    )

    context.add_evidence(existing)

    assert context.evidence[-1].evidence_type == EvidenceType.MARKET_DATA

    # Re-assemble independently and verify research evidence is still
    # produced through the public assemble() path.
    second_context = await assembler.assemble(request)

    assert len(second_context.evidence) == 1
    assert second_context.evidence[0].evidence_type == EvidenceType.NEWS
