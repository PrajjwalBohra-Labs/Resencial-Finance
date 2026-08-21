from datetime import datetime
from typing import Any, Sequence

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)
from backend.app.domain.research_sources import (
    BondRecord,
    BondYieldRecord,
    FilingRecord,
    MacroObservation,
    NewsRecord,
)
from backend.app.schemas.market import ReturnAnalysis


def _dump_model(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump()

    if isinstance(value, dict):
        return value.copy()

    raise TypeError(
        f"Expected a Pydantic model or dictionary, got {type(value).__name__}."
    )


def _format_analysis(analysis: ReturnAnalysis) -> str:
    summary = analysis.price_summary

    return "\n".join(
        [
            "Deterministic analysis:",
            f"Absolute return: {analysis.absolute_return}",
            f"Percentage return: {analysis.percentage_return}%",
            f"CAGR: {analysis.cagr}%",
            f"Maximum drawdown: {analysis.maximum_drawdown}%",
            f"Annualised volatility: {analysis.annualised_volatility}%",
            f"Starting price: {summary.starting_price}",
            f"Latest price: {summary.latest_price}",
            f"Highest close: {summary.highest_close}",
            f"Lowest close: {summary.lowest_close}",
        ]
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
    analysis: ReturnAnalysis | None = None,
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

    if analysis is not None:
        content = f"{content}\n\n{_format_analysis(analysis)}"

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

def create_news_evidence(record: NewsRecord) -> Evidence:
    """Convert a normalized news record into research evidence."""

    content_parts = []

    if record.summary:
        content_parts.append(record.summary)

    if record.category:
        content_parts.append(f"Category: {record.category}")

    content = "\n".join(content_parts) or record.title

    return Evidence(
        evidence_type=EvidenceType.NEWS,
        title=record.title,
        content=content,
        source=EvidenceSource(
            name=record.source_name,
            url=record.url,
            published_at=record.published_at,
            retrieved_at=record.retrieved_at,
            provider=record.provider,
        ),
        symbol=record.symbol.upper() if record.symbol else None,
        confidence=1.0,
    )


def create_filing_evidence(record: FilingRecord) -> Evidence:
    """Convert a normalized filing record into research evidence."""

    content_parts = [
        f"Filing type: {record.filing_type}",
    ]

    if record.filing_date is not None:
        content_parts.append(
            f"Filing date: {record.filing_date.isoformat()}"
        )

    if record.summary:
        content_parts.append(record.summary)

    return Evidence(
        evidence_type=EvidenceType.FILING,
        title=record.title,
        content="\n".join(content_parts),
        source=EvidenceSource(
            name=record.source_name,
            url=record.url,
            published_at=record.published_at,
            retrieved_at=record.retrieved_at,
            provider=record.provider,
        ),
        symbol=record.symbol.upper(),
        confidence=1.0,
    )


def create_macro_evidence(record: MacroObservation) -> Evidence:
    """Convert a normalized macro observation into research evidence."""

    content_parts = [
        f"Series: {record.series_name}",
        f"Observation date: {record.observation_date.isoformat()}",
        f"Value: {record.value}",
    ]

    if record.unit:
        content_parts.append(f"Unit: {record.unit}")

    return Evidence(
        evidence_type=EvidenceType.MACRO,
        title=record.series_name,
        content="\n".join(content_parts),
        source=EvidenceSource(
            name=record.source_name,
            url=record.url,
            published_at=None,
            retrieved_at=record.retrieved_at,
            provider=record.provider,
        ),
        confidence=1.0,
    )


def create_bond_evidence(record: BondRecord) -> Evidence:
    """Convert a normalized bond record into research evidence."""

    content_parts = [
        f"Identifier: {record.identifier}",
    ]

    if record.issuer:
        content_parts.append(f"Issuer: {record.issuer}")

    if record.isin:
        content_parts.append(f"ISIN: {record.isin}")

    if record.coupon_rate is not None:
        content_parts.append(
            f"Coupon rate: {record.coupon_rate}%"
        )

    if record.maturity_date is not None:
        content_parts.append(
            f"Maturity date: {record.maturity_date.isoformat()}"
        )

    if record.credit_rating:
        content_parts.append(
            f"Credit rating: {record.credit_rating}"
        )

    return Evidence(
        evidence_type=EvidenceType.REGULATORY,
        title=record.title,
        content="\n".join(content_parts),
        source=EvidenceSource(
            name=record.source_name,
            url=record.url,
            published_at=record.published_at,
            retrieved_at=record.retrieved_at,
            provider=record.provider,
        ),
        confidence=1.0,
    )


def create_bond_yield_evidence(record: BondYieldRecord) -> Evidence:
    """Convert a normalized bond-yield observation into research evidence."""

    content_parts = [
        f"Identifier: {record.identifier}",
        f"Yield: {record.yield_value}{record.yield_unit}",
    ]

    if record.observation_date is not None:
        content_parts.append(
            f"Observation date: {record.observation_date.isoformat()}"
        )

    return Evidence(
        evidence_type=EvidenceType.MACRO,
        title=f"{record.identifier} bond yield",
        content="\n".join(content_parts),
        source=EvidenceSource(
            name=record.source_name,
            url=record.url,
            published_at=None,
            retrieved_at=record.retrieved_at,
            provider=record.provider,
        ),
        confidence=1.0,
    )

