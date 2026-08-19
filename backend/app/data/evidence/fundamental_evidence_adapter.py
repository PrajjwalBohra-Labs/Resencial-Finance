from datetime import datetime, timezone
from typing import Any

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)
from backend.app.domain.research import ResearchRequest
from backend.app.schemas.fundamentals import (
    FundamentalAnalysis,
    FundamentalPeriod,
)
from backend.app.services.fundamentals_service import FundamentalsService


class FundamentalEvidenceAdapter:
    """Transforms raw fundamentals into compact research-grade evidence."""

    def __init__(
        self,
        fundamentals_service: FundamentalsService,
    ) -> None:
        self._fundamentals_service = fundamentals_service

    _MAPPINGS = {
        "revenue": (
            "Total Revenue",
            "Operating Revenue",
        ),
        "net_income": (
            "Net Income",
            "Net Income Common Stockholders",
        ),
        "basic_eps": (
            "Basic EPS",
        ),
        "diluted_eps": (
            "Diluted EPS",
        ),
        "total_assets": (
            "Total Assets",
        ),
        "stockholders_equity": (
            "Stockholders Equity",
            "Common Stock Equity",
        ),
        "net_loans": (
            "Net Loan",
        ),
        "operating_cash_flow": (
            "Operating Cash Flow",
        ),
        "free_cash_flow": (
            "Free Cash Flow",
        ),
    }

    @classmethod
    def _value(
        cls,
        row: dict[str, object],
        field: str,
    ) -> float | None:
        for candidate in cls._MAPPINGS[field]:
            value = row.get(candidate)

            if value is None:
                continue

            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        return None

    @classmethod
    def _period(
        cls,
        row: dict[str, object],
    ) -> FundamentalPeriod:
        return FundamentalPeriod(
            period=str(row.get("period", "")),
            revenue=cls._value(row, "revenue"),
            net_income=cls._value(row, "net_income"),
            basic_eps=cls._value(row, "basic_eps"),
            diluted_eps=cls._value(row, "diluted_eps"),
            total_assets=cls._value(row, "total_assets"),
            stockholders_equity=cls._value(
                row,
                "stockholders_equity",
            ),
            net_loans=cls._value(row, "net_loans"),
            operating_cash_flow=cls._value(
                row,
                "operating_cash_flow",
            ),
            free_cash_flow=cls._value(
                row,
                "free_cash_flow",
            ),
        )

    @staticmethod
    def _growth(
        latest: float | None,
        previous: float | None,
    ) -> float | None:
        if latest is None or previous is None or previous == 0:
            return None

        return ((latest / previous) - 1) * 100

    @classmethod
    def _analysis(
        cls,
        *,
        periods: list[FundamentalPeriod],
        ratios: dict[str, object],
    ) -> FundamentalAnalysis:
        latest = periods[0] if periods else None
        previous = periods[1] if len(periods) > 1 else None

        def ratio(name: str) -> float | None:
            value = ratios.get(name)

            if value is None:
                return None

            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        return FundamentalAnalysis(
            latest_period=latest.period if latest else None,
            previous_period=previous.period if previous else None,
            revenue_growth=cls._growth(
                latest.revenue if latest else None,
                previous.revenue if previous else None,
            ),
            net_income_growth=cls._growth(
                latest.net_income if latest else None,
                previous.net_income if previous else None,
            ),
            basic_eps_growth=cls._growth(
                latest.basic_eps if latest else None,
                previous.basic_eps if previous else None,
            ),
            diluted_eps_growth=cls._growth(
                latest.diluted_eps if latest else None,
                previous.diluted_eps if previous else None,
            ),
            asset_growth=cls._growth(
                latest.total_assets if latest else None,
                previous.total_assets if previous else None,
            ),
            equity_growth=cls._growth(
                latest.stockholders_equity if latest else None,
                previous.stockholders_equity if previous else None,
            ),
            trailing_pe=ratio("trailingPE"),
            forward_pe=ratio("forwardPE"),
            price_to_book=ratio("priceToBook"),
            return_on_equity=(
                None
                if ratio("returnOnEquity") is None
                else ratio("returnOnEquity") * 100
            ),
            return_on_assets=(
                None
                if ratio("returnOnAssets") is None
                else ratio("returnOnAssets") * 100
            ),
            profit_margin=(
                None
                if ratio("profitMargins") is None
                else ratio("profitMargins") * 100
            ),
            operating_margin=(
                None
                if ratio("operatingMargins") is None
                else ratio("operatingMargins") * 100
            ),
            revenue_growth_reported=(
                None
                if ratio("revenueGrowth") is None
                else ratio("revenueGrowth") * 100
            ),
            earnings_growth_reported=(
                None
                if ratio("earningsGrowth") is None
                else ratio("earningsGrowth") * 100
            ),
            dividend_yield=ratio("dividendYield"),
            market_cap=ratio("marketCap"),
            enterprise_value=ratio("enterpriseValue"),
            currency=(
                str(ratios["currency"])
                if ratios.get("currency") is not None
                else None
            ),
            observations=periods,
        )

    @staticmethod
    def _format_number(value: float | None) -> str:
        if value is None:
            return "insufficient data"

        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))

            return f"{value:.4f}".rstrip("0").rstrip(".")

        return str(value)

    @staticmethod
    def _format_financial_value(value: float | None) -> str:
        """Format financial statement values while preserving decimal precision."""
        if value is None:
            return "insufficient data"

        return f"{float(value):.1f}"
    @classmethod
    def _format_analysis(
        cls,
        analysis: FundamentalAnalysis,
    ) -> str:
        currency = analysis.currency or "currency not supplied"

        lines = [
            "Deterministic fundamental analysis:",
            f"Latest period: {analysis.latest_period or 'unknown'}",
            f"Previous period: {analysis.previous_period or 'unknown'}",
            f"Currency: {currency}",
            f"Revenue growth: {cls._format_number(analysis.revenue_growth)}%",
            f"Net income growth: {cls._format_number(analysis.net_income_growth)}%",
            f"Basic EPS growth: {cls._format_number(analysis.basic_eps_growth)}%",
            f"Diluted EPS growth: {cls._format_number(analysis.diluted_eps_growth)}%",
            f"Asset growth: {cls._format_number(analysis.asset_growth)}%",
            f"Equity growth: {cls._format_number(analysis.equity_growth)}%",
            "",
            "Key ratios:",
            f"Trailing P/E: {cls._format_number(analysis.trailing_pe)}",
            f"Forward P/E: {cls._format_number(analysis.forward_pe)}",
            f"Price/book: {cls._format_number(analysis.price_to_book)}",
            f"ROE: {cls._format_number(analysis.return_on_equity)}%",
            f"ROA: {cls._format_number(analysis.return_on_assets)}%",
            f"Profit margin: {cls._format_number(analysis.profit_margin)}%",
            f"Operating margin: {cls._format_number(analysis.operating_margin)}%",
            f"Reported revenue growth: {cls._format_number(analysis.revenue_growth_reported)}%",
            f"Reported earnings growth: {cls._format_number(analysis.earnings_growth_reported)}%",
            f"Dividend yield: {cls._format_number(analysis.dividend_yield)}%",
            f"Market capitalization: {cls._format_number(analysis.market_cap)}",
            f"Enterprise value: {cls._format_number(analysis.enterprise_value)}",
        ]

        return "\n".join(lines)

    @classmethod
    def _format_income_statement(
        cls,
        period: FundamentalPeriod,
    ) -> list[str]:
        return [
            "Latest income statement:",
            f"Period: {period.period}",
            f"Total Revenue: {cls._format_financial_value(period.revenue)}",
            f"Net Income: {cls._format_financial_value(period.net_income)}",
            f"Basic EPS: {cls._format_financial_value(period.basic_eps)}",
            f"Diluted EPS: {cls._format_financial_value(period.diluted_eps)}",
        ]

    @classmethod
    def _format_balance_sheet(
        cls,
        period: FundamentalPeriod,
    ) -> list[str]:
        return [
            "Latest balance sheet:",
            f"Period: {period.period}",
            f"Total Assets: {cls._format_financial_value(period.total_assets)}",
            (
                "Stockholders Equity: "
                f"{cls._format_financial_value(period.stockholders_equity)}"
            ),
            f"Net Loans: {cls._format_financial_value(period.net_loans)}",
        ]

    @classmethod
    def _format_cash_flow(
        cls,
        period: FundamentalPeriod,
    ) -> list[str]:
        return [
            "Latest cash flow:",
            f"Period: {period.period}",
            (
                "Operating Cash Flow: "
                f"{cls._format_financial_value(period.operating_cash_flow)}"
            ),
            (
                "Free Cash Flow: "
                f"{cls._format_financial_value(period.free_cash_flow)}"
            ),
        ]

    @classmethod
    def _format_previous_period(
        cls,
        period: FundamentalPeriod,
    ) -> list[str]:
        return [
            "Previous period:",
            f"Period: {period.period}",
            f"Total Revenue: {cls._format_financial_value(period.revenue)}",
            f"Net Income: {cls._format_financial_value(period.net_income)}",
            f"Basic EPS: {cls._format_financial_value(period.basic_eps)}",
            f"Diluted EPS: {cls._format_financial_value(period.diluted_eps)}",
            f"Total Assets: {cls._format_financial_value(period.total_assets)}",
            (
                "Stockholders Equity: "
                f"{cls._format_financial_value(period.stockholders_equity)}"
            ),
            f"Net Loans: {cls._format_financial_value(period.net_loans)}",
            (
                "Operating Cash Flow: "
                f"{cls._format_financial_value(period.operating_cash_flow)}"
            ),
            (
                "Free Cash Flow: "
                f"{cls._format_financial_value(period.free_cash_flow)}"
            ),
        ]

    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        if not request.symbols:
            return []

        retrieved_at = datetime.now(timezone.utc)
        evidence: list[Evidence] = []

        for symbol in request.symbols:
            income = await (
                self._fundamentals_service.get_income_statement(symbol)
            )
            balance = await (
                self._fundamentals_service.get_balance_sheet(symbol)
            )
            cash_flow = await (
                self._fundamentals_service.get_cash_flow(symbol)
            )
            ratios = await (
                self._fundamentals_service.get_key_ratios(symbol)
            )

            income_periods = [
                self._period(row)
                for row in income
            ]

            balance_periods = {
                str(row.get("period")): row
                for row in balance
            }

            cash_flow_periods = {
                str(row.get("period")): row
                for row in cash_flow
            }

            periods: list[FundamentalPeriod] = []

            for period in income_periods:
                balance_row = balance_periods.get(period.period, {})
                cash_row = cash_flow_periods.get(period.period, {})

                periods.append(
                    period.model_copy(
                        update={
                            "total_assets": (
                                period.total_assets
                                if period.total_assets is not None
                                else self._value(
                                    balance_row,
                                    "total_assets",
                                )
                            ),
                            "stockholders_equity": (
                                period.stockholders_equity
                                if period.stockholders_equity is not None
                                else self._value(
                                    balance_row,
                                    "stockholders_equity",
                                )
                            ),
                            "net_loans": self._value(
                                balance_row,
                                "net_loans",
                            ),
                            "operating_cash_flow": self._value(
                                cash_row,
                                "operating_cash_flow",
                            ),
                            "free_cash_flow": self._value(
                                cash_row,
                                "free_cash_flow",
                            ),
                        }
                    )
                )

            analysis = self._analysis(
                periods=periods,
                ratios=ratios,
            )

            sections = [
                f"Fundamental evidence for {symbol.upper()}.",
                "",
                self._format_analysis(analysis),
            ]

            if periods:
                latest = periods[0]

                sections.extend(
                    [
                        "",
                        *self._format_income_statement(latest),
                        "",
                        *self._format_balance_sheet(latest),
                        "",
                        *self._format_cash_flow(latest),
                    ]
                )

            if len(periods) > 1:
                sections.extend(
                    [
                        "",
                        *self._format_previous_period(periods[1]),
                    ]
                )

            evidence.append(
                Evidence(
                    evidence_type=EvidenceType.FUNDAMENTAL,
                    title=f"{symbol.upper()} fundamental analysis",
                    content="\n".join(sections),
                    source=EvidenceSource(
                        name="Yahoo Finance",
                        provider=self._fundamentals_service.provider_name,
                        retrieved_at=retrieved_at,
                    ),
                    symbol=symbol.upper(),
                    exchange=(
                        request.exchange.upper()
                        if request.exchange
                        else None
                    ),
                    confidence=1.0,
                )
            )

        return evidence



