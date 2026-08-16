from datetime import datetime, timezone
from typing import Any

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)
from backend.app.domain.research import ResearchRequest
from backend.app.ports.market_evidence import MarketEvidencePort
from backend.app.services.fundamentals_service import FundamentalsService


class FundamentalEvidenceAdapter:
    """Builds research evidence from company fundamentals."""

    def __init__(
        self,
        fundamentals_service: FundamentalsService,
    ) -> None:
        self._fundamentals_service = fundamentals_service

    @staticmethod
    def _format_section(
        title: str,
        rows: list[dict[str, object]],
    ) -> str:
        if not rows:
            return f"{title}:\nNo data available."

        lines = [f"{title}:"]

        for index, row in enumerate(rows, start=1):
            lines.append(f"Observation {index}: {row}")

        return "\n".join(lines)

    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        evidence: list[Evidence] = []

        if not request.symbols:
            return evidence

        retrieved_at = datetime.now(timezone.utc)

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

            sections = [
                self._format_section(
                    "Income statement",
                    income_statement,
                ),
                self._format_section(
                    "Balance sheet",
                    balance_sheet,
                ),
                self._format_section(
                    "Cash flow",
                    cash_flow,
                ),
                (
                    "Key ratios:\n"
                    f"{key_ratios}"
                    if key_ratios
                    else "Key ratios:\nNo data available."
                ),
            ]

            content = "\n\n".join(sections)

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
                    confidence=1.0,
                )
            )

        return evidence
