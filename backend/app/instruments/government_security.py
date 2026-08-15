from datetime import date

from pydantic import ConfigDict

from backend.app.instruments.base import Instrument, InstrumentType


class GovernmentSecurity(Instrument):
    model_config = ConfigDict(extra="forbid")

    instrument_type: InstrumentType = InstrumentType.GOVERNMENT_SECURITY
    isin: str | None = None
    coupon_rate: float | None = None
    maturity_date: date | None = None
