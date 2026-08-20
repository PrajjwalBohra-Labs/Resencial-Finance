from datetime import date

import pytest

from backend.app.domain.research import ResearchFocus, ResearchRequest
from backend.app.schemas.market import HistoricalPrice
from backend.app.services.research_analytics_service import (
    ResearchAnalyticsService,
)


def create_prices() -> list[HistoricalPrice]:
    return [
        HistoricalPrice(
            date="2026-08-10",
            open=100.0,
            high=102.0,
            low=99.0,
            close=100.0,
            volume=1000000,
        ),
        HistoricalPrice(
            date="2026-08-11",
            open=100.0,
            high=112.0,
            low=99.0,
            close=110.0,
            volume=1100000,
        ),
        HistoricalPrice(
            date="2026-08-12",
            open=110.0,
            high=133.0,
            low=109.0,
            close=132.0,
            volume=1200000,
        ),
    ]


def test_market_analytics_generates_findings() -> None:
    findings = ResearchAnalyticsService.analyse_prices(
        symbol="HDFCBANK",
        prices=create_prices(),
    )

    assert findings
    assert any(
        finding.category.value == "growth"
        for finding in findings
    )
    assert any(
        finding.category.value == "trend"
        for finding in findings
    )
    assert any(
        finding.category.value == "distribution"
        for finding in findings
    )


def test_findings_have_evidence_references() -> None:
    findings = ResearchAnalyticsService.analyse_prices(
        symbol="HDFCBANK",
        prices=create_prices(),
    )

    assert findings
    assert all(
        "market:HDFCBANK" in finding.evidence_refs
        for finding in findings
    )


def test_findings_have_uncertainty() -> None:
    findings = ResearchAnalyticsService.analyse_prices(
        symbol="HDFCBANK",
        prices=create_prices(),
    )

    assert findings
    assert all(
        finding.uncertainty
        for finding in findings
    )


def test_insufficient_prices_return_no_findings() -> None:
    findings = ResearchAnalyticsService.analyse_prices(
        symbol="HDFCBANK",
        prices=[
            HistoricalPrice(
                date="2026-08-10",
                open=100.0,
                high=101.0,
                low=99.0,
                close=100.0,
                volume=1000000,
            )
        ],
    )

    assert findings == []
