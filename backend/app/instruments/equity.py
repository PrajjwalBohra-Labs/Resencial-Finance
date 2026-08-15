from pydantic import ConfigDict

from backend.app.instruments.base import Instrument, InstrumentType


class Equity(Instrument):
    model_config = ConfigDict(extra="forbid")

    instrument_type: InstrumentType = InstrumentType.EQUITY
    isin: str | None = None
    sector: str | None = None
    industry: str | None = None
