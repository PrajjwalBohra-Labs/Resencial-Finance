from datetime import datetime
from typing import Any, Sequence

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)


def _dump_model(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump()

    if isinstance(value, dict):
        return value.copy()

    raise TypeError(
        f"Expected a Pydantic model or dictionary, got {type(value).__name__}."
    )


def create_market_evidence(
    *,
    symbol: str,
    exchange: str,
    prices: Sequence[Any],
    provider: str,
    source_name: str,
    retrieved_at: datetime,
    source_url: str | None = None,
) -> Evidence:
    if not prices:
        raise ValueError("prices must contain at least one observation.")

    observations = [
        _dump_model(price)
        for price in prices
    ]

    return Evidence(
        evidence_type=EvidenceType.MARKET_DATA,
        title=f"{symbol.upper()} market price history",
        content=(
            f"Historical market price observations for "
            f"{symbol.upper()} on {exchange.upper()}.\n\n"
            f"Observations:\n{observations}"
        ),
        source=EvidenceSource(
            name=source_name,
            url=source_url,
            retrieved_at=retrieved_at,
            provider=provider,
        ),
        symbol=symbol.upper(),
        exchange=exchange.upper(),
        confidence=1.0,
    )
