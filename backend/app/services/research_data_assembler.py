from datetime import date, datetime, timezone

from backend.app.domain.evidence_factory import create_market_evidence
from backend.app.domain.research import ResearchContext, ResearchRequest
from backend.app.services.market_service import MarketService


class ResearchDataAssembler:
    """Builds an ephemeral research context from live data sources."""

    def __init__(self, market_service: MarketService) -> None:
        self._market_service = market_service

    async def assemble_market_context(
        self,
        *,
        request: ResearchRequest,
        start_date: date,
        end_date: date,
    ) -> ResearchContext:
        if start_date > end_date:
            raise ValueError(
                "start_date must be before or equal to end_date."
            )

        context = ResearchContext(request=request)

        exchange = request.exchange or "NSE"

        for symbol in request.symbols:
            prices = await self._market_service.get_historical_prices(
                symbol=symbol,
                exchange=exchange,
                start_date=start_date,
                end_date=end_date,
            )

            if not prices:
                continue

            evidence = create_market_evidence(
                symbol=symbol,
                exchange=exchange,
                prices=prices,
                provider=self._market_service.provider_name,
                source_name=self._market_service.provider_name,
                retrieved_at=datetime.now(timezone.utc),
            )

            context.add_evidence(evidence)

        return context
