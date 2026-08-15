from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class InstrumentType(StrEnum):
    EQUITY = "equity"
    BOND = "bond"
    GOVERNMENT_SECURITY = "government_security"
    T_BILL = "t_bill"
    ETF = "etf"
    REIT = "reit"
    INVIT = "invit"


class Instrument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    name: str
    instrument_type: InstrumentType
    exchange: str | None = None
    currency: str = "INR"
    issuer: str | None = None
