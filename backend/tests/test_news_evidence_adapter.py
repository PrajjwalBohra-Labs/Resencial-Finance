from datetime import date, datetime, timezone

import pytest

from backend.app.data.evidence.news_evidence_adapter import NewsEvidenceAdapter
from backend.app.domain.research import ResearchRequest
from backend.app.domain.research_sources import NewsRecord


class FakeNewsProvider:
    name = "fake-news"

    def __init__(self) -> None:
        self.company_calls: list[dict[str, object]] = []
        self.search_calls: list[dict[str, object]] = []

    async def get_company_news(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[NewsRecord]:
        self.company_calls.append(
            {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        return [
            NewsRecord(
                title=f"{symbol} earnings update",
                source_name="Test News",
                url="https://example.com/news",
                published_at=datetime(
                    2026,
                    8,
                    11,
                    tzinfo=timezone.utc,
                ),
                retrieved_at=datetime(
                    2026,
                    8,
                    12,
                    tzinfo=timezone.utc,
                ),
                provider=self.name,
                symbol=symbol,
                summary=f"{symbol} reported updated results.",
                category="earnings",
            )
        ]

    async def search_news(
        self,
        query: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[NewsRecord]:
        self.search_calls.append(
            {
                "query": query,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        return [
            NewsRecord(
                title="Market research result",
                source_name="Test News",
                retrieved_at=datetime(
                    2026,
                    8,
                    12,
                    tzinfo=timezone.utc,
                ),
                provider=self.name,
                summary="Relevant market information.",
            )
        ]


@pytest.mark.asyncio
async def test_news_adapter_collects_company_news() -> None:
    provider = FakeNewsProvider()
    adapter = NewsEvidenceAdapter(provider)

    request = ResearchRequest(
        question="Analyse HDFC Bank news.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    evidence = await adapter.collect(request)

    assert len(evidence) == 1
    assert evidence[0].evidence_type.value == "news"
    assert evidence[0].symbol == "HDFCBANK"
    assert evidence[0].source_name == "Test News"
    assert evidence[0].url == "https://example.com/news"

    assert provider.company_calls == [
        {
            "symbol": "HDFCBANK",
            "start_date": date(2026, 8, 10),
            "end_date": date(2026, 8, 11),
        }
    ]

    assert provider.search_calls == []


@pytest.mark.asyncio
async def test_news_adapter_supports_multiple_symbols() -> None:
    provider = FakeNewsProvider()
    adapter = NewsEvidenceAdapter(provider)

    request = ResearchRequest(
        question="Compare company news.",
        symbols=["HDFCBANK", "ICICIBANK"],
        exchange="NSE",
    )

    evidence = await adapter.collect(request)

    assert len(evidence) == 2
    assert [item.symbol for item in evidence] == [
        "HDFCBANK",
        "ICICIBANK",
    ]

    assert [call["symbol"] for call in provider.company_calls] == [
        "HDFCBANK",
        "ICICIBANK",
    ]


@pytest.mark.asyncio
async def test_news_adapter_falls_back_to_search_without_company_results() -> None:
    provider = FakeNewsProvider()

    async def empty_company_news(
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[NewsRecord]:
        return []

    provider.get_company_news = empty_company_news  # type: ignore[method-assign]

    adapter = NewsEvidenceAdapter(provider)

    request = ResearchRequest(
        question="Indian banking sector news",
        symbols=["HDFCBANK"],
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    evidence = await adapter.collect(request)

    assert len(evidence) == 1
    assert evidence[0].evidence_type.value == "news"
    assert evidence[0].title == "Market research result"

    assert provider.search_calls == [
        {
            "query": "Indian banking sector news",
            "start_date": date(2026, 8, 10),
            "end_date": date(2026, 8, 11),
        }
    ]
