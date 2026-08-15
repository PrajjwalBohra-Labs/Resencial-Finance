from dataclasses import dataclass

from backend.app.instruments.base import InstrumentType


class InstrumentResolutionError(ValueError):
    """Raised when an instrument cannot be resolved."""


@dataclass(frozen=True)
class ResolvedInstrument:
    symbol: str
    exchange: str | None
    instrument_type: InstrumentType
    provider_symbol: str


class InstrumentResolver:
    """Resolves Resencial Finance instrument identities to provider symbols."""

    def resolve_equity(
        self,
        symbol: str,
        exchange: str,
    ) -> ResolvedInstrument:
        normalized_symbol = symbol.strip().upper()
        normalized_exchange = exchange.strip().upper()

        if not normalized_symbol:
            raise InstrumentResolutionError(
                "Instrument symbol cannot be empty."
            )

        if normalized_exchange not in {"NSE", "BSE"}:
            raise InstrumentResolutionError(
                f"Unsupported exchange '{normalized_exchange}'."
            )

        suffix = {
            "NSE": ".NS",
            "BSE": ".BO",
        }[normalized_exchange]

        provider_symbol = (
            normalized_symbol
            if normalized_symbol.endswith(suffix)
            else f"{normalized_symbol}{suffix}"
        )

        return ResolvedInstrument(
            symbol=normalized_symbol,
            exchange=normalized_exchange,
            instrument_type=InstrumentType.EQUITY,
            provider_symbol=provider_symbol,
        )


resolver = InstrumentResolver()
