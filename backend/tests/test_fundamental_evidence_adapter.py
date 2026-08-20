from datetime import datetime, timezone

import pytest

from backend.app.domain.research import ResearchRequest
from backend.app.services.fundamentals_service import FundamentalsService
from backend.app.data.evidence.fundamental_evidence_adapter import (
    FundamentalEvidenceAdapter,
)


class FakeFundamentalsProvider:
    name = "fake_fundamentals"

    async def get_income_statement(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        return [
            {
                "period": "2026-03-31",
                "Total Revenue": 1200.0,
                "Net Income": 240.0,
                "Basic EPS": 24.0,
                "Diluted EPS": 23.5,
            },
            {
                "period": "2025-03-31",
                "Total Revenue": 1000.0,
                "Net Income": 200.0,
                "Basic EPS": 20.0,
                "Diluted EPS": 19.0,
            },
        ]

    async def get_balance_sheet(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        return [
            {
                "period": "2026-03-31",
                "Total Assets": 10000.0,
                "Stockholders Equity": 1500.0,
                "Net Loan": 7000.0,
            },
            {
                "period": "2025-03-31",
                "Total Assets": 9000.0,
                "Stockholders Equity": 1250.0,
                "Net Loan": 6200.0,
            },
        ]

    async def get_cash_flow(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        return [
            {
                "period": "2026-03-31",
                "Operating Cash Flow": 300.0,
                "Free Cash Flow": 250.0,
            },
            {
                "period": "2025-03-31",
                "Operating Cash Flow": 275.0,
                "Free Cash Flow": 225.0,
            },
        ]

    async def get_key_ratios(
        self,
        symbol: str,
    ) -> dict[str, object]:
        return {
            "currency": "INR",
            "marketCap": 1500000.0,
            "enterpriseValue": 1700000.0,
            "trailingPE": 15.5,
            "forwardPE": 13.0,
            "priceToBook": 2.1,
            "returnOnEquity": 0.15,
            "returnOnAssets": 0.018,
            "profitMargins": 0.20,
            "operatingMargins": 0.31,
            "revenueGrowth": 0.12,
            "earningsGrowth": 0.15,
            "dividendYield": 0.02,
        }


@pytest.mark.asyncio
async def test_fundamental_evidence_is_compact_and_deterministic() -> None:
    service = FundamentalsService(FakeFundamentalsProvider())
    adapter = FundamentalEvidenceAdapter(service)

    context_request = ResearchRequest(
        question="Analyse HDFC Bank fundamentals.",
        symbols=["HDFCBANK"],
        exchange="NSE",
    )

    evidence = await adapter.collect(context_request)

    assert len(evidence) == 1

    item = evidence[0]

    assert item.evidence_type.value == "fundamental"
    assert item.symbol == "HDFCBANK"
    assert item.exchange == "NSE"

    assert "Currency: INR" in item.content
    assert "Revenue growth: 20%" in item.content
    assert "Net income growth: 20%" in item.content
    assert "Basic EPS growth: 20%" in item.content
    assert "Trailing P/E: 15.5" in item.content
    assert "ROE: 15%" in item.content

    assert "Total Revenue: ₹1,200" in item.content
    assert "Net Income: ₹240" in item.content

    assert "Fake" not in item.content



