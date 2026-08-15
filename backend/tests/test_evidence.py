from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)


def create_source() -> EvidenceSource:
    return EvidenceSource(
        name="Yahoo Finance",
        url="https://finance.yahoo.com/",
        retrieved_at=datetime.now(timezone.utc),
        provider="yahoo_finance",
    )


def test_evidence_source() -> None:
    source = create_source()

    assert source.name == "Yahoo Finance"
    assert source.provider == "yahoo_finance"


def test_market_data_evidence() -> None:
    evidence = Evidence(
        evidence_type=EvidenceType.MARKET_DATA,
        title="HDFC Bank historical prices",
        content="Historical NSE price observations.",
        source=create_source(),
        symbol="HDFCBANK",
        exchange="NSE",
    )

    assert evidence.evidence_type == EvidenceType.MARKET_DATA
    assert evidence.symbol == "HDFCBANK"
    assert evidence.exchange == "NSE"
    assert evidence.confidence == 1.0


def test_evidence_rejects_invalid_confidence() -> None:
    with pytest.raises(ValidationError):
        Evidence(
            evidence_type=EvidenceType.NEWS,
            title="Test",
            content="Test content",
            source=create_source(),
            confidence=1.5,
        )


def test_evidence_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Evidence(
            evidence_type=EvidenceType.NEWS,
            title="Test",
            content="Test content",
            source=create_source(),
            unexpected_field="not allowed",
        )
