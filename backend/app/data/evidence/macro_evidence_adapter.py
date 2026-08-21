from backend.app.data.providers.macro import MacroDataProvider
from backend.app.domain.evidence import Evidence
from backend.app.domain.evidence_factory import create_macro_evidence
from backend.app.domain.research import ResearchRequest
from backend.app.ports.macro_evidence import MacroEvidencePort


class MacroEvidenceAdapter(MacroEvidencePort):
    """Convert normalized macro-provider observations into research evidence."""

    def __init__(self, provider: MacroDataProvider) -> None:
        self._provider = provider

    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        query = request.question.strip()

        if not query:
            return []

        observations = await self._provider.get_series(
            series_name=query,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        return [
            create_macro_evidence(observation)
            for observation in observations
        ]
