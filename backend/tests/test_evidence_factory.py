from datetime import datetime, timezone

import pytest

from backend.app.domain.evidence import EvidenceType
from backend.app.domain.evidence_factory import create_market_evidence


def create_prices() -> list[dict[str, object]]:
    return [
        {
            "date": "2026-08-10",
            "open": 748.0,
            "high": 752.0,
            "low": 745.0,
            "close": 750.0,
            "volume": 1000000,
        },
        {
            "date": "2026-08-11",
            "open": 750.0,
            "high": 758.0,
            "low": 749.0,
            "close": 755.0,
            "volume": 1200000,
        },
    ]


def test_create_market_evidence() -> None:
    retrieved_at = datetime(
        2026,
        8,
        15,
        10,
        0,
        tzinfo=timezone.utc,
    )

    evidence = create_market_evidence(
        symbol="HDFCBANK",
        exchange="NSE",
        prices=create_prices(),
        provider="yahoo_finance",
        source_name="Yahoo Finance",
        retrieved_at=retrieved_at,
    )

    assert evidence.evidence_type == EvidenceType.MARKET_DATA
    assert evidence.symbol == "HDFCBANK"
    assert evidence.exchange == "NSE"
    assert evidence.source.provider == "yahoo_finance"
    assert evidence.source.name == "Yahoo Finance"
    assert evidence.source.retrieved_at == retrieved_at
    assert evidence.confidence == 1.0
    assert "2026-08-10" in evidence.content
    assert "755.0" in evidence.content


def test_create_market_evidence_normalizes_identity() -> None:
    evidence = create_market_evidence(
        symbol="hdfcbank",
        exchange="nse",
        prices=create_prices(),
        provider="yahoo_finance",
        source_name="Yahoo Finance",
        retrieved_at=datetime.now(timezone.utc),
    )

    assert evidence.symbol == "HDFCBANK"
    assert evidence.exchange == "NSE"


def test_create_market_evidence_requires_prices() -> None:
    with pytest.raises(
        ValueError,
        match="prices must contain at least one observation",
    ):
        create_market_evidence(
            symbol="HDFCBANK",
            exchange="NSE",
            prices=[],
            provider="yahoo_finance",
            source_name="Yahoo Finance",
            retrieved_at=datetime.now(timezone.utc),
        )


def test_create_market_evidence_accepts_pydantic_models() -> None:
    from pydantic import BaseModel

    class Price(BaseModel):
        date: str
        close: float

    evidence = create_market_evidence(
        symbol="HDFCBANK",
        exchange="NSE",
        prices=[
            Price(
                date="2026-08-14",
                close=727.0,
            )
        ],
        provider="test_provider",
        source_name="Test Provider",
        retrieved_at=datetime.now(timezone.utc),
    )

    assert evidence.evidence_type == EvidenceType.MARKET_DATA
    assert "2026-08-14" in evidence.content
    assert "727.0" in evidence.content
