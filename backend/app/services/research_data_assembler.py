from datetime import date, datetime, timezone
from typing import Any

from backend.app.domain.evidence_factory import create_market_evidence
from backend.app.domain.research import ResearchContext, ResearchRequest
from backend.app.schemas.market import HistoricalPrice
from backend.app.services.market_analysis_service import MarketAnalysisService
from backend.app.services.fundamentals_service import FundamentalsService
from backend.app.services.market_service import MarketService
from backend.app.services.research_analytics_service import ResearchAnalyticsService
from backend.app.services.benchmark_resolver import benchmark_resolver
from backend.app.services.relationship_analysis_service import RelationshipAnalysisService
from backend.app.services.relationship_finding_service import RelationshipFindingService
from backend.app.data.evidence.fundamental_evidence_adapter import FundamentalEvidenceAdapter


class ResearchDataAssembler:
    """Builds an ephemeral research context from available data sources."""

    def __init__(
        self,
        market_service: MarketService,
        fundamentals_service: FundamentalsService | None = None,
    ) -> None:
        self._market_service = market_service
        self._fundamentals_service = fundamentals_service

    @staticmethod
    def _normalize_prices(
        prices: list[Any],
    ) -> list[HistoricalPrice]:
        return [
            price
            if isinstance(price, HistoricalPrice)
            else HistoricalPrice.model_validate(price)
            for price in prices
        ]

    @staticmethod
    def _format_analysis(
        analysis: Any,
    ) -> str:
        cagr = (
            f"{analysis.cagr}%"
            if analysis.cagr is not None
            else "insufficient data"
        )

        volatility = (
            f"{analysis.annualised_volatility}%"
            if analysis.annualised_volatility is not None
            else "insufficient data"
        )

        daily_changes = "\n".join(
            (
                f"{item.date}: "
                f"change={item.open_to_close_change}; "
                f"change_percentage="
                f"{item.open_to_close_change_percentage}%"
            )
            for item in analysis.daily_changes
        )

        period = analysis.period_summary

        return "\n".join(
            [
                "Deterministic analysis:",
                f"Absolute return: {analysis.absolute_return}",
                f"Percentage return: {analysis.percentage_return}%",
                f"CAGR: {cagr}",
                f"Maximum drawdown: {analysis.maximum_drawdown}%",
                f"Annualised volatility: {volatility}",
                "",
                "Price summary:",
                (
                    "Starting price: "
                    f"{analysis.price_summary.starting_price}"
                ),
                (
                    "Latest price: "
                    f"{analysis.price_summary.latest_price}"
                ),
                (
                    "Highest close: "
                    f"{analysis.price_summary.highest_close}"
                ),
                (
                    "Lowest close: "
                    f"{analysis.price_summary.lowest_close}"
                ),
                "",
                "Daily open-to-close changes:",
                daily_changes,
                "",
                "Period summary:",
                f"Period high: {period.period_high}",
                f"Period low: {period.period_low}",
                f"Total volume: {period.total_volume}",
                (
                    "Average daily volume: "
                    f"{period.average_daily_volume}"
                ),
            ]
        )

    async def assemble(
        self,
        request: ResearchRequest,
    ) -> ResearchContext:
        context = ResearchContext(request=request)

        if not request.symbols:
            return context

        if (
            request.focus.value in {
                "general",
                "market",
                "comparison",
                "risk",
                "fixed_income",
                "macro",
            }
            and request.start_date is not None
            and request.end_date is not None
        ):
            context = await self.assemble_market_context(
                request=request,
                start_date=request.start_date,
                end_date=request.end_date,
            )

        if (
            self._fundamentals_service is not None
            and request.focus.value in {
                "general",
                "fundamental",
                "valuation",
            }
        ):
            adapter = FundamentalEvidenceAdapter(
                self._fundamentals_service
            )

            fundamental_evidence = await adapter.collect(request)

            for item in fundamental_evidence:
                context.add_evidence(item)

        return context

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

        asset_prices_by_symbol: dict[str, list[HistoricalPrice]] = {}

        # ------------------------------------------------------------
        # 1. Collect asset market evidence and deterministic findings.
        # ------------------------------------------------------------
        for symbol in request.symbols:
            raw_prices = await self._market_service.get_historical_prices(
                symbol=symbol,
                exchange=exchange,
                start_date=start_date,
                end_date=end_date,
            )

            prices = self._normalize_prices(raw_prices)

            if not prices:
                continue

            asset_prices_by_symbol[symbol] = prices

            analysis = MarketAnalysisService.analyse_prices(
                prices
            )

            evidence = create_market_evidence(
                symbol=symbol,
                exchange=exchange,
                prices=prices,
                provider=self._market_service.provider_name,
                source_name=self._market_service.provider_name,
                retrieved_at=datetime.now(timezone.utc),
            )

            evidence = evidence.model_copy(
                update={
                    "content": (
                        f"{evidence.content}\n\n"
                        f"{self._format_analysis(analysis)}"
                    )
                }
            )

            context.add_evidence(evidence)

            findings = ResearchAnalyticsService.analyse_prices(
                symbol=symbol,
                prices=prices,
            )

            for finding in findings:
                context.add_finding(finding)

        # ------------------------------------------------------------
        # 2. Resolve and fetch the exchange benchmark exactly once.
        # ------------------------------------------------------------
        if not asset_prices_by_symbol:
            return context

        benchmark = benchmark_resolver.resolve(exchange)

        benchmark_raw_prices = (
            await self._market_service.get_historical_prices(
                symbol=benchmark.symbol,
                exchange=benchmark.exchange,
                start_date=start_date,
                end_date=end_date,
            )
        )

        benchmark_prices = self._normalize_prices(
            benchmark_raw_prices
        )

        if len(benchmark_prices) < 2:
            return context

        benchmark_analysis = MarketAnalysisService.analyse_prices(
            benchmark_prices
        )

        benchmark_evidence = create_market_evidence(
            symbol=benchmark.symbol,
            exchange=benchmark.exchange,
            prices=benchmark_prices,
            provider=self._market_service.provider_name,
            source_name=self._market_service.provider_name,
            retrieved_at=datetime.now(timezone.utc),
            analysis=benchmark_analysis,
        )

        benchmark_evidence = benchmark_evidence.model_copy(
            update={
                "title": (
                    f"{benchmark.name} benchmark market history"
                ),
                "content": (
                    f"{benchmark_evidence.content}\n\n"
                    f"Benchmark rationale: {benchmark.rationale}"
                ),
            }
        )

        context.add_evidence(benchmark_evidence)

        # ------------------------------------------------------------
        # 3. Compare every collected asset against the same benchmark.
        # ------------------------------------------------------------
        for symbol, prices in asset_prices_by_symbol.items():
            relationship = RelationshipAnalysisService.analyse(
                prices,
                benchmark_prices,
            )

            relationship_findings = RelationshipFindingService.build(
                asset_symbol=symbol,
                benchmark_symbol=benchmark.symbol,
                relationship=relationship,
                asset_evidence_ref=f"market:{symbol}",
                benchmark_evidence_ref=(
                    f"benchmark:{benchmark.symbol}"
                ),
            )

            for relationship_finding in relationship_findings:
                context.add_finding(relationship_finding)

        return context

