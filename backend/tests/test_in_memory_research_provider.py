from datetime import date, datetime, timezone

import pytest

from backend.app.data.providers.in_memory_research import (
    InMemoryResearchProvider,
)
from backend.app.domain.research_sources import (
    BondRecord,
    BondYieldRecord,
    FilingRecord,
    MacroObservation,
    NewsRecord,
)


def _retrieved_at() -> datetime:
    return datetime(2026, 8, 21, tzinfo=timezone.utc)


def _news(
    title: str,
    symbol: str,
    published_at: datetime,
) -> NewsRecord:
    return NewsRecord(
        title=title,
        source_name="Test News",
        published_at=published_at,
        retrieved_at=_retrieved_at(),
        provider="test",
        symbol=symbol,
        summary=f"Summary for {title}",
    )


def _filing(
    filing_type: str,
    filing_date: date,
) -> FilingRecord:
    return FilingRecord(
        title=filing_type,
        source_name="Test Filing Source",
        retrieved_at=_retrieved_at(),
        provider="test",
        symbol="HDFCBANK",
        filing_type=filing_type,
        filing_date=filing_date,
    )


def _macro(
    observation_date: date,
    value: float,
) -> MacroObservation:
    return MacroObservation(
        series_name="CPI",
        observation_date=observation_date,
        value=value,
        unit="percent",
        source_name="Test Macro Source",
        retrieved_at=_retrieved_at(),
        provider="test",
    )


def _bond(identifier: str, issuer: str) -> BondRecord:
    return BondRecord(
        title=identifier,
        source_name="Test Bond Source",
        retrieved_at=_retrieved_at(),
        provider="test",
        identifier=identifier,
        issuer=issuer,
    )


@pytest.mark.asyncio
async def test_news_search_and_company_news() -> None:
    provider = InMemoryResearchProvider(
        news=[
            _news(
                "HDFC Bank earnings",
                "HDFCBANK",
                datetime(2026, 8, 20, tzinfo=timezone.utc),
            ),
            _news(
                "ICICI Bank earnings",
                "ICICIBANK",
                datetime(2026, 8, 20, tzinfo=timezone.utc),
            ),
        ],
    )

    results = await provider.search_news("HDFC")
    assert len(results) == 1
    assert results[0].symbol == "HDFCBANK"

    company_news = await provider.get_company_news("hdfcbank")
    assert len(company_news) == 1


@pytest.mark.asyncio
async def test_filings_return_latest_and_date_filtered_records() -> None:
    provider = InMemoryResearchProvider(
        filings=[
            _filing("Annual Report", date(2025, 6, 30)),
            _filing("Quarterly Result", date(2026, 6, 30)),
        ],
    )

    results = await provider.search_filings(
        "hdfcbank",
        start_date=date(2026, 1, 1),
    )

    assert len(results) == 1
    assert results[0].filing_type == "Quarterly Result"

    latest = await provider.get_latest_filing("HDFCBANK")
    assert latest is not None
    assert latest.filing_type == "Quarterly Result"


@pytest.mark.asyncio
async def test_macro_series_and_latest_observation() -> None:
    provider = InMemoryResearchProvider(
        macro=[
            _macro(date(2026, 7, 1), 3.1),
            _macro(date(2026, 8, 1), 3.2),
        ],
    )

    results = await provider.get_series(
        "cpi",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 8, 1),
    )

    assert len(results) == 2

    latest = await provider.get_latest("CPI")
    assert latest is not None
    assert latest.value == 3.2


@pytest.mark.asyncio
async def test_bond_search_and_latest_yield() -> None:
    provider = InMemoryResearchProvider(
        bonds=[
            _bond("GOI-2034", "Government of India"),
            _bond("HDFC-2031", "HDFC Bank"),
        ],
        bond_yields=[
            BondYieldRecord(
                identifier="GOI-2034",
                yield_value=7.05,
                observation_date=date(2026, 8, 20),
                source_name="Test Bond Source",
                retrieved_at=_retrieved_at(),
                provider="test",
            ),
            BondYieldRecord(
                identifier="GOI-2034",
                yield_value=7.10,
                observation_date=date(2026, 8, 21),
                source_name="Test Bond Source",
                retrieved_at=_retrieved_at(),
                provider="test",
            ),
        ],
    )

    result = await provider.get_bond("GOI-2034")
    assert result is not None
    assert result.issuer == "Government of India"

    search = await provider.search_bonds("government")
    assert len(search) == 1

    latest_yield = await provider.get_bond_yield("GOI-2034")
    assert latest_yield is not None
    assert latest_yield.yield_value == 7.10
