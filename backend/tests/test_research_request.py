from datetime import date

import pytest
from pydantic import ValidationError

from backend.app.domain.research import (
    ResearchFocus,
    ResearchRequest,
)


def test_research_request_supports_date_range() -> None:
    request = ResearchRequest(
        question="Analyse HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        focus=ResearchFocus.MARKET,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 8, 15),
    )

    assert request.start_date == date(2026, 7, 1)
    assert request.end_date == date(2026, 8, 15)


def test_research_request_allows_missing_date_range() -> None:
    request = ResearchRequest(
        question="Analyse HDFC Bank.",
        symbols=["HDFCBANK"],
    )

    assert request.start_date is None
    assert request.end_date is None


def test_research_request_rejects_invalid_date_range() -> None:
    with pytest.raises(
        ValidationError,
        match="start_date must be before or equal to end_date",
    ):
        ResearchRequest(
            question="Analyse HDFC Bank.",
            symbols=["HDFCBANK"],
            start_date=date(2026, 8, 15),
            end_date=date(2026, 7, 1),
        )


def test_research_request_allows_same_start_and_end_date() -> None:
    request = ResearchRequest(
        question="What happened today?",
        symbols=["HDFCBANK"],
        start_date=date(2026, 8, 15),
        end_date=date(2026, 8, 15),
    )

    assert request.start_date == request.end_date


def test_research_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ResearchRequest(
            question="Analyse HDFC Bank.",
            unknown_field="not allowed",
        )
