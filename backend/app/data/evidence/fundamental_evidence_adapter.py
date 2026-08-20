from pydantic import BaseModel
from backend.app.domain.fundamentals import IncomeStatement, ValuationMetrics
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
            "net_loan",
            "net_loans",
            "Net Loan",
            "Net Loans",
            "netLoan",
            "netLoans",
        ),
        "operating_cash_flow": (
            "Operating Cash Flow",
        ),
        "free_cash_flow": (
            "Free Cash Flow",
        ),
    }
    def _value(
        self,
        row: object,
        field: str,
    ) -> float | None:
        aliases = {
            "total_assets": (
                "total_assets",
                "Total Assets",
                "totalAssets",
            ),
            "stockholders_equity": (
                "stockholders_equity",
                "Stockholders Equity",
                "Common Stock Equity",
                "stockholdersEquity",
            ),
            "net_loans": (
                "net_loans",
                "Net Loan",
                "Net Loans",
                "netLoan",
                "netLoans",
            ),
            "operating_cash_flow": (
                "operating_cash_flow",
                "Operating Cash Flow",
                "operatingCashFlow",
            ),
            "free_cash_flow": (
                "free_cash_flow",
                "Free Cash Flow",
                "freeCashFlow",
            ),
            "revenue": (
                "revenue",
                "Revenue",
                "Total Revenue",
                "total_revenue",
                "totalRevenue",
            ),
            "net_income": (
                "net_income",
                "Net Income",
                "netIncome",
            ),
            "basic_eps": (
                "basic_eps",
                "Basic EPS",
                "basicEps",
            ),
            "diluted_eps": (
                "diluted_eps",
                "Diluted EPS",
                "dilutedEps",
            ),
        }

        candidates = aliases.get(field, (field,))

        if isinstance(row, BaseModel):
            value = None

            for candidate in candidates:
                candidate_value = getattr(row, candidate, None)

                if candidate_value is not None:
                    value = candidate_value
                    break

        elif isinstance(row, dict):
            value = None

            for candidate in candidates:
                if candidate in row and row[candidate] is not None:
                    value = row[candidate]
                    break

        else:
            value = None

            for candidate in candidates:
                candidate_value = getattr(row, candidate, None)

                if candidate_value is not None:
                    value = candidate_value
                    break

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None



    @staticmethod
    def _growth(
        current: float | None,
        previous: float | None,
    ) -> float | None:
        if current is None or previous is None:
            return None

        if previous == 0:
            return None

        return ((current - previous) / previous) * 100
    @classmethod
    def _analysis(
        cls,
        *,
        periods: list[FundamentalPeriod],
        ratios: ValuationMetrics | dict[str, object],
    ) -> FundamentalAnalysis:
        latest = periods[0] if periods else None
        previous = periods[1] if len(periods) > 1 else None

        def ratio(name: str) -> float | None:
            field_map = {
                "marketCap": (
                    "market_capitalization",
                    "marketCap",
                    "market_cap",
                ),
                "enterpriseValue": (
                    "enterprise_value",
                    "enterpriseValue",
                    "enterprise_value",
                ),
                "trailingPE": (
                    "trailing_pe",
                    "trailingPE",
                ),
                "forwardPE": (
                    "forward_pe",
                    "forwardPE",
                ),
                "priceToBook": (
                    "price_to_book",
                    "priceToBook",
                ),
                "dividendYield": (
                    "dividend_yield",
                    "dividendYield",
                ),
            }

            candidates = field_map.get(name, (name,))
            value = None

            if isinstance(ratios, BaseModel):
                for field in candidates:
                    candidate = getattr(ratios, field, None)

                    if candidate is not None:
                        value = candidate
                        break

            elif isinstance(ratios, dict):
                for field in candidates:
                    if field in ratios and ratios[field] is not None:
                        value = ratios[field]
                        break

            else:
                for field in candidates:
                    candidate = getattr(ratios, field, None)

                    if candidate is not None:
                        value = candidate
                        break

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
            currency="INR",
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
    def _format_indian_number(value: float) -> str:
        """Format a numeric value using the Indian numbering system."""
        number = f"{float(value):.1f}"

        integer_part, decimal_part = number.split(".")

        sign = ""
        if integer_part.startswith("-"):
            sign = "-"
            integer_part = integer_part[1:]

        if len(integer_part) <= 3:
            grouped = integer_part
        else:
            last_three = integer_part[-3:]
            remaining = integer_part[:-3]

            groups = []

            while len(remaining) > 2:
                groups.insert(0, remaining[-2:])
                remaining = remaining[:-2]

            if remaining:
                groups.insert(0, remaining)

            grouped = ",".join(groups + [last_three])

        if decimal_part == "0":
            return f"{sign}{grouped}"

        return f"{sign}{grouped}.{decimal_part}"

    @classmethod
    def _format_financial_value(
        cls,
        value: float | None,
    ) -> str:
        """Format financial values using Indian comma grouping."""
        if value is None:
            return "insufficient data"

        return f"₹{cls._format_indian_number(value)}"
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

    def _period(
        self,
        row: object,
    ) -> FundamentalPeriod:
        if isinstance(row, BaseModel):
            period = row.period.period_end.date().isoformat()
            revenue = getattr(row, "total_revenue", None)
            net_income = getattr(row, "net_income", None)
            basic_eps = getattr(row, "basic_eps", None)
            diluted_eps = getattr(row, "diluted_eps", None)
        elif isinstance(row, dict):
            period = str(row.get("period", ""))

            revenue = self._value(row, "revenue")
            if revenue is None:
                revenue = self._value(row, "Total Revenue")

            net_income = self._value(row, "net_income")
            if net_income is None:
                net_income = self._value(row, "Net Income")

            basic_eps = self._value(row, "basic_eps")
            if basic_eps is None:
                basic_eps = self._value(row, "Basic EPS")

            diluted_eps = self._value(row, "diluted_eps")
            if diluted_eps is None:
                diluted_eps = self._value(row, "Diluted EPS")
        else:
            period = ""
            revenue = None
            net_income = None
            basic_eps = None
            diluted_eps = None

        return FundamentalPeriod(
            period=period,
            revenue=revenue,
            net_income=net_income,
            basic_eps=basic_eps,
            diluted_eps=diluted_eps,
            total_assets=None,
            stockholders_equity=None,
            net_loans=None,
            operating_cash_flow=None,
            free_cash_flow=None,
        )
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
                (
                    row.period.period_end.date().isoformat()
                    if isinstance(row, BaseModel)
                    else str(row.get("period", ""))
                ): row
                for row in balance
            }

            cash_flow_periods = {
                (
                    row.period.period_end.date().isoformat()
                    if isinstance(row, BaseModel)
                    else str(row.get("period", ""))
                ): row
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




















