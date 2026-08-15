from datetime import datetime, timezone

from backend.app.domain.evidence import Evidence
from backend.app.domain.evidence_factory import create_market_evidence
from backend.app.domain.research import ResearchRequest
from backend.app.ports.market_evidence import MarketEvidencePort
from backend.app.services.market_service import MarketService


class MarketEvidenceAdapter(MarketEvidencePort):
    def __init__(self, market_service: MarketService) -> None:
        self._market_service = market_service

    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        evidence: list[Evidence] = []

        if not request.symbols:
            return evidence

        if request.exchange is None:
            return evidence

        if request.start_date is None or request.end_date is None:
            return evidence

        for symbol in request.symbols:
            history = await self._market_service.get_historical_prices(
                symbol=symbol,
                exchange=request.exchange,
                start_date=request.start_date,
                end_date=request.end_date,
            )

            for item in history:
                evidence.append(
                    create_market_evidence(
                        symbol=symbol,
                        exchange=request.exchange,
                        prices=[item],
                        provider=self._market_service.provider_name,
                        source_name=self._market_service.provider_name,
                        retrieved_at=datetime.now(timezone.utc),
                    )
                )

        return evidence
