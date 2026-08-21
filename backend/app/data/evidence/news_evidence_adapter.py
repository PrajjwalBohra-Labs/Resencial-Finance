from datetime import date, datetime, timezone

from backend.app.data.providers.news import NewsProvider
from backend.app.domain.evidence import Evidence
from backend.app.domain.evidence_factory import create_news_evidence
from backend.app.domain.research import ResearchRequest
from backend.app.ports.news_evidence import NewsEvidencePort


class NewsEvidenceAdapter(NewsEvidencePort):
    """Convert normalized news-provider records into research evidence."""

    def __init__(self, provider: NewsProvider) -> None:
        self._provider = provider

    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        if not request.symbols and not request.question.strip():
            return []

        records = []

        if request.symbols:
            for symbol in request.symbols:
                records.extend(
                    await self._provider.get_company_news(
                        symbol=symbol,
                        start_date=request.start_date,
                        end_date=request.end_date,
                    )
                )

        if not records:
            records = await self._provider.search_news(
                query=request.question,
                start_date=request.start_date,
                end_date=request.end_date,
            )

        return [
            create_news_evidence(record)
            for record in records
        ]
