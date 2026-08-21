from backend.app.data.providers.filings import FilingsProvider
from backend.app.domain.evidence import Evidence
from backend.app.domain.evidence_factory import create_filing_evidence
from backend.app.domain.research import ResearchRequest
from backend.app.ports.filing_evidence import FilingEvidencePort


class FilingEvidenceAdapter(FilingEvidencePort):
    """Convert normalized filing-provider records into research evidence."""

    def __init__(self, provider: FilingsProvider) -> None:
        self._provider = provider

    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        if not request.symbols:
            return []

        evidence: list[Evidence] = []

        for symbol in request.symbols:
            records = await self._provider.search_filings(
                symbol=symbol,
                start_date=request.start_date,
                end_date=request.end_date,
            )

            evidence.extend(
                create_filing_evidence(record)
                for record in records
            )

        return evidence
