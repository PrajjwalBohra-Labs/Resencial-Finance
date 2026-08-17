from datetime import datetime, timezone

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)
from backend.app.domain.research import ResearchRequest
from backend.app.services.fundamentals_service import FundamentalsService


class FundamentalEvidenceAdapter:
    """Builds compact research evidence from company fundamentals."""

    _INCOME_FIELDS = (
        "Total Revenue",
        "Net Income",
        "Basic EPS",
        "Diluted EPS",
        "Net Interest Income",
        "Interest Income",
        "Interest Expense",
    )

    _BALANCE_FIELDS = (
        "Total Assets",
        "Total Liabilities Net Minority Interest",
        "Stockholders Equity",
        "Common Stock Equity",
        "Net Loan",
        "Cash And Cash Equivalents",
        "Tangible Book Value",
    )

    _CASH_FLOW_FIELDS = (
        "Operating Cash Flow",
        "Free Cash Flow",
        "Capital Expenditure",
        "Cash Dividends Paid",
        "Changes In Cash",
    )

    _RATIO_FIELDS = (
        "marketCap",
        "enterpriseValue",
        "trailingPE",
        "forwardPE",
        "priceToBook",
        "returnOnEquity",
        "returnOnAssets",
        "profitMargins",
        "operatingMargins",
        "revenueGrowth",
        "earningsGrowth",
        "dividendYield",
    )

    def __init__(
        self,
        fundamentals_service: FundamentalsService,
    ) -> None:
        self._fundamentals_service = fundamentals_service

    @staticmethod
    def _format_value(
        label: str,
        value: object,
        *,
        percentage: bool = False,
    ) -> str:
        if percentage and isinstance(value, (int, float)):
            return f"{label}: {float(value) * 100}%"

        return f"{label}: {value}"

    @staticmethod
    def _latest_row(
        rows: list[dict[str, object]],
    ) -> dict[str, object] | None:
        return rows[0] if rows else None

    @staticmethod
    def _previous_row(
        rows: list[dict[str, object]],
    ) -> dict[str, object] | None:
        return rows[1] if len(rows) >= 2 else None

    @classmethod
    def _format_statement(
        cls,
        *,
        title: str,
        rows: list[dict[str, object]],
        fields: tuple[str, ...],
    ) -> str:
        latest = cls._latest_row(rows)

        if latest is None:
            return f"{title}:\nNo data available."

        lines = [
            f"{title}:",
            f"Period: {latest.get('period', 'unknown')}",
        ]

        for field in fields:
            value = latest.get(field)

            if value is not None:
                lines.append(
                    cls._format_value(
                        field,
                        value,
                    )
                )

        return "\n".join(lines)

    @classmethod
    def _format_period_comparison(
        cls,
        rows: list[dict[str, object]],
    ) -> str:
        latest = cls._latest_row(rows)
        previous = cls._previous_row(rows)

        if latest is None:
            return "Period comparison:\nNo data available."

        if previous is None:
            return (
                "Period comparison:\n"
                "Insufficient historical observations."
            )

        lines = [
            "Period comparison:",
            f"Latest period: {latest.get('period', 'unknown')}",
            f"Previous period: {previous.get('period', 'unknown')}",
        ]

        for field, label in (
            ("Total Revenue", "Revenue"),
            ("Net Income", "Net income"),
            ("Basic EPS", "Basic EPS"),
            ("Diluted EPS", "Diluted EPS"),
        ):
            current = latest.get(field)
            prior = previous.get(field)

            if not isinstance(current, (int, float)):
                continue

            if not isinstance(prior, (int, float)):
                continue

            if prior == 0:
                continue

            change = (
                (float(current) - float(prior))
                / float(prior)
            ) * 100

            lines.append(
                f"{label} change: {change:.4f}%"
            )

        return "\n".join(lines)

    @classmethod
    def _format_ratios(
        cls,
        ratios: dict[str, object],
    ) -> str:
        if not ratios:
            return "Key ratios:\nNo data available."

        labels = {
            "marketCap": "Market capitalization",
            "enterpriseValue": "Enterprise value",
            "trailingPE": "Trailing P/E",
            "forwardPE": "Forward P/E",
            "priceToBook": "Price/book",
            "returnOnEquity": "Return on equity",
            "returnOnAssets": "Return on assets",
            "profitMargins": "Profit margin",
            "operatingMargins": "Operating margin",
            "revenueGrowth": "Revenue growth",
            "earningsGrowth": "Earnings growth",
            "dividendYield": "Dividend yield",
        }

        percentage_fields = {
            "returnOnEquity",
            "returnOnAssets",
            "profitMargins",
            "operatingMargins",
            "revenueGrowth",
            "earningsGrowth",
        }

        lines = ["Key ratios:"]

        for field in cls._RATIO_FIELDS:
            value = ratios.get(field)

            if value is None:
                continue

            if field == "dividendYield":
                lines.append(
                    f"{labels.get(field, field)}: {value}%"
                )
            else:
                lines.append(
                    cls._format_value(
                        labels.get(field, field),
                        value,
                        percentage=field in percentage_fields,
                    )
                )

        return "\n".join(lines)

    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        if not request.symbols:
            return []

        retrieved_at = datetime.now(timezone.utc)
        evidence: list[Evidence] = []

        for symbol in request.symbols:
            income_statement = (
                await self._fundamentals_service.get_income_statement(
                    symbol
                )
            )
            balance_sheet = (
                await self._fundamentals_service.get_balance_sheet(
                    symbol
                )
            )
            cash_flow = (
                await self._fundamentals_service.get_cash_flow(
                    symbol
                )
            )
            key_ratios = (
                await self._fundamentals_service.get_key_ratios(
                    symbol
                )
            )

            content = "\n\n".join(
                [
                    "Fundamental evidence:",
                    "Currency: INR",
                    self._format_statement(
                        title="Latest income statement",
                        rows=income_statement,
                        fields=self._INCOME_FIELDS,
                    ),
                    self._format_period_comparison(
                        income_statement
                    ),
                    self._format_statement(
                        title="Latest balance sheet",
                        rows=balance_sheet,
                        fields=self._BALANCE_FIELDS,
                    ),
                    self._format_statement(
                        title="Latest cash flow",
                        rows=cash_flow,
                        fields=self._CASH_FLOW_FIELDS,
                    ),
                    self._format_ratios(key_ratios),
                ]
            )

            evidence.append(
                Evidence(
                    evidence_type=EvidenceType.FUNDAMENTAL,
                    title=f"{symbol.upper()} fundamental data",
                    content=content,
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


