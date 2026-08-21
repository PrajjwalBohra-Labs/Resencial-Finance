from datetime import date, datetime, timezone
from unittest.mock import AsyncMock

import pytest

from backend.app.domain.evidence import Evidence, EvidenceSource, EvidenceType
from backend.app.domain.research import ResearchFocus, ResearchRequest
from backend.app.services.research_data_assembler import ResearchDataAssembler


def make_evidence(evidence_type: EvidenceType) -> Evidence:
    now = datetime.now(timezone.utc)

    return Evidence(
        evidence_type=evidence_type,
        title=f"{evidence_type.value} evidence",
        content="test evidence",
        source=EvidenceSource(
            name="test-provider",
            url=None,
            published_at=None,
            retrieved_at=now,
            provider="test-provider",
        ),
    )


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


@pytest.fixture
def request_base() -> ResearchRequest:
    return ResearchRequest(
        question="test research question",
        symbols=["TEST"],
        exchange="NSE",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )


def build_assembler(
    *,
    focus: ResearchFocus,
    request: ResearchRequest,
):
    news_port = AsyncMock()
    filing_port = AsyncMock()
    macro_port = AsyncMock()
    bond_port = AsyncMock()

    news_port.collect.return_value = [
        make_evidence(EvidenceType.NEWS)
    ]
    filing_port.collect.return_value = [
        make_evidence(EvidenceType.FILING)
    ]
    macro_port.collect.return_value = [
        make_evidence(EvidenceType.MACRO)
    ]
    bond_port.collect.return_value = [
        make_evidence(EvidenceType.REGULATORY)
    ]

    request = request.model_copy(
        update={"focus": focus}
    )

    assembler = ResearchDataAssembler(
        market_service=FakeMarketService(),
        news_evidence_port=news_port,
        filing_evidence_port=filing_port,
        macro_evidence_port=macro_port,
        bond_evidence_port=bond_port,
    )

    return assembler, request, {
        "news": news_port,
        "filing": filing_port,
        "macro": macro_port,
        "bond": bond_port,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "focus,expected",
    [
        (
            ResearchFocus.MARKET,
            {"news": True, "filing": False, "macro": False, "bond": False},
        ),
        (
            ResearchFocus.RISK,
            {"news": True, "filing": False, "macro": False, "bond": False},
        ),
        (
            ResearchFocus.COMPARISON,
            {"news": True, "filing": False, "macro": False, "bond": False},
        ),
        (
            ResearchFocus.FUNDAMENTAL,
            {"news": False, "filing": True, "macro": False, "bond": False},
        ),
        (
            ResearchFocus.VALUATION,
            {"news": False, "filing": True, "macro": False, "bond": False},
        ),
        (
            ResearchFocus.MACRO,
            {"news": False, "filing": False, "macro": True, "bond": False},
        ),
        (
            ResearchFocus.FIXED_INCOME,
            {"news": False, "filing": False, "macro": False, "bond": True},
        ),
    ],
)
async def test_specialized_focus_routes_to_expected_port(
    request_base: ResearchRequest,
    focus: ResearchFocus,
    expected: dict[str, bool],
) -> None:
    assembler, request, ports = build_assembler(
        focus=focus,
        request=request_base,
    )

    context = await assembler._collect_research_evidence(request)

    for name, should_call in expected.items():
        if should_call:
            ports[name].collect.assert_awaited_once_with(request)
        else:
            ports[name].collect.assert_not_awaited()

    assert len(context) == 1


@pytest.mark.asyncio
async def test_general_focus_collects_all_research_ports(
    request_base: ResearchRequest,
) -> None:
    assembler, request, ports = build_assembler(
        focus=ResearchFocus.GENERAL,
        request=request_base,
    )

    evidence = await assembler._collect_research_evidence(request)

    ports["news"].collect.assert_awaited_once_with(request)
    ports["filing"].collect.assert_awaited_once_with(request)
    ports["macro"].collect.assert_awaited_once_with(request)
    ports["bond"].collect.assert_awaited_once_with(request)

    assert len(evidence) == 4
