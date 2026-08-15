from pydantic import ConfigDict

from backend.app.instruments.base import Instrument, InstrumentType


class ETF(Instrument):
    model_config = ConfigDict(extra="forbid")

    instrument_type: InstrumentType = InstrumentType.ETF
    isin: str | None = None
    underlying_index: str | None = None
