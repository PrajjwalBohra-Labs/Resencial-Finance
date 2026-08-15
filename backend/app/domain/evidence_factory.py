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

    normalized_symbol = symbol.upper()
    normalized_exchange = exchange.upper()

    if len(observations) == 1:
        observation = observations[0]

        fields = [
            f"{field.replace('_', ' ').title()}: {value}"
            for field, value in observation.items()
        ]

        content = "; ".join(fields)
        title = f"{normalized_symbol} market price"
    else:
        content = (
            f"Historical market price observations for "
            f"{normalized_symbol} on {normalized_exchange}.\n\n"
            f"Observations:\n{observations}"
        )

        title = f"{normalized_symbol} market price history"

    return Evidence(
        evidence_type=EvidenceType.MARKET_DATA,
        title=title,
        content=content,
        source=EvidenceSource(
            name=source_name,
            url=source_url,
            retrieved_at=retrieved_at,
            provider=provider,
        ),
        symbol=normalized_symbol,
        exchange=normalized_exchange,
        confidence=1.0,
    )
