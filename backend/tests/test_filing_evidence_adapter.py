from datetime import date, datetime, timezone

import pytest

from backend.app.data.evidence.filing_evidence_adapter import (
    FilingEvidenceAdapter,
)
from backend.app.domain.research import ResearchRequest
from backend.app.domain.research_sources import FilingRecord


class FakeFilingsProvider:
    name = "fake-filings"

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def search_filings(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[FilingRecord]:
        self.calls.append(
            {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        return [
            FilingRecord(
                title=f"{symbol} annual filing",
                source_name="fake-regulator",
                url=f"https://example.test/{symbol}",
                published_at=datetime(
                    2026,
                    8,
                    11,
                    tzinfo=timezone.utc,
                ),
                retrieved_at=datetime.now(timezone.utc),
                provider=self.name,
                symbol=symbol,
                filing_type="annual_report",
                filing_date=date(2026, 8, 11),
                summary=f"Summary for {symbol}.",
            )
        ]


@pytest.mark.asyncio
async def test_filing_adapter_returns_empty_for_missing_symbols() -> None:
    provider = FakeFilingsProvider()
    adapter = FilingEvidenceAdapter(provider)

    request = ResearchRequest(
        question="Research filings.",
        symbols=[],
    )

    evidence = await adapter.collect(request)

    assert evidence == []
    assert provider.calls == []


@pytest.mark.asyncio
async def test_filing_adapter_converts_records_to_evidence() -> None:
    provider = FakeFilingsProvider()
    adapter = FilingEvidenceAdapter(provider)

    request = ResearchRequest(
        question="Research HDFC Bank filings.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 11),
    )

    evidence = await adapter.collect(request)

    assert len(evidence) == 1

    item = evidence[0]

    assert item.evidence_type.value == "filing"
    assert item.title == "HDFCBANK annual filing"
    assert item.symbol == "HDFCBANK"
    assert item.source.name == "fake-regulator"
    assert item.source.url == "https://example.test/HDFCBANK"
    assert "Filing type: annual_report" in item.content
    assert "Filing date: 2026-08-11" in item.content
    assert "Summary for HDFCBANK." in item.content


@pytest.mark.asyncio
async def test_filing_adapter_passes_date_range_to_provider() -> None:
    provider = FakeFilingsProvider()
    adapter = FilingEvidenceAdapter(provider)

    request = ResearchRequest(
        question="Research filings.",
        symbols=["HDFCBANK"],
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 11),
    )

    await adapter.collect(request)

    assert provider.calls == [
        {
            "symbol": "HDFCBANK",
            "start_date": date(2026, 8, 1),
            "end_date": date(2026, 8, 11),
        }
    ]


@pytest.mark.asyncio
async def test_filing_adapter_collects_multiple_symbols() -> None:
    provider = FakeFilingsProvider()
    adapter = FilingEvidenceAdapter(provider)

    request = ResearchRequest(
        question="Compare filings.",
        symbols=["HDFCBANK", "ICICIBANK"],
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 11),
    )

    evidence = await adapter.collect(request)

    assert len(evidence) == 2
    assert [item.symbol for item in evidence] == [
        "HDFCBANK",
        "ICICIBANK",
    ]

    assert [call["symbol"] for call in provider.calls] == [
        "HDFCBANK",
        "ICICIBANK",
    ]
