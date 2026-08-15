from datetime import date

from pydantic import ConfigDict

from backend.app.instruments.base import Instrument, InstrumentType


class TBill(Instrument):
    model_config = ConfigDict(extra="forbid")

    instrument_type: InstrumentType = InstrumentType.T_BILL
    isin: str | None = None
    maturity_date: date | None = None
    face_value: float | None = None
