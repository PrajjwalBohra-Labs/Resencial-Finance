from pydantic import ConfigDict

from backend.app.instruments.base import Instrument, InstrumentType


class REIT(Instrument):
    model_config = ConfigDict(extra="forbid")

    instrument_type: InstrumentType = InstrumentType.REIT
    isin: str | None = None
    sector: str | None = None
