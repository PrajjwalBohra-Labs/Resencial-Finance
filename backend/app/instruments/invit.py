from pydantic import ConfigDict

from backend.app.instruments.base import Instrument, InstrumentType


class InvIT(Instrument):
    model_config = ConfigDict(extra="forbid")

    instrument_type: InstrumentType = InstrumentType.INVIT
    isin: str | None = None
    sector: str | None = None
