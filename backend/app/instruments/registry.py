from backend.app.instruments.base import Instrument


class InstrumentRegistry:
    def __init__(self) -> None:
        self._instruments: dict[str, Instrument] = {}

    def register(self, instrument: Instrument) -> None:
        self._instruments[instrument.symbol] = instrument

    def get(self, symbol: str) -> Instrument | None:
        return self._instruments.get(symbol)

    def all(self) -> list[Instrument]:
        return list(self._instruments.values())


registry = InstrumentRegistry()


__all__ = [
    "InstrumentRegistry",
    "registry",
]
