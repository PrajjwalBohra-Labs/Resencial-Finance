from datetime import date

from pydantic import ConfigDict

from backend.app.instruments.base import Instrument, InstrumentType


class Bond(Instrument):
    model_config = ConfigDict(extra="forbid")

    instrument_type: InstrumentType = InstrumentType.BOND
    isin: str | None = None
    coupon_rate: float | None = None
    maturity_date: date | None = None
    credit_rating: str | None = None
    rating_outlook: str | None = None
