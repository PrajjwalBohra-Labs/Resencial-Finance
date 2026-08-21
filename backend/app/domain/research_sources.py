from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ResearchSourceRecord(BaseModel):
    """Common normalized metadata for external research records."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    url: str | None = None
    published_at: datetime | None = None
    retrieved_at: datetime
    provider: str = Field(min_length=1)


class NewsRecord(ResearchSourceRecord):
    """Normalized financial-news record."""

    symbol: str | None = None
    summary: str = ""
    category: str | None = None


class FilingRecord(ResearchSourceRecord):
    """Normalized company or regulatory filing record."""

    symbol: str
    filing_type: str = Field(min_length=1)
    filing_date: date | None = None
    summary: str = ""


class MacroObservation(BaseModel):
    """Normalized macroeconomic observation."""

    model_config = ConfigDict(extra="forbid")

    series_name: str = Field(min_length=1)
    observation_date: date
    value: float
    unit: str | None = None
    source_name: str = Field(min_length=1)
    url: str | None = None
    retrieved_at: datetime
    provider: str = Field(min_length=1)


class BondRecord(ResearchSourceRecord):
    """Normalized fixed-income instrument record."""

    identifier: str = Field(min_length=1)
    issuer: str | None = None
    isin: str | None = None
    coupon_rate: float | None = None
    maturity_date: date | None = None
    credit_rating: str | None = None


class BondYieldRecord(BaseModel):
    """Normalized bond-yield observation."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(min_length=1)
    yield_value: float
    yield_unit: str = "%"
    observation_date: date | None = None
    source_name: str = Field(min_length=1)
    url: str | None = None
    retrieved_at: datetime
    provider: str = Field(min_length=1)


__all__ = [
    "BondRecord",
    "BondYieldRecord",
    "FilingRecord",
    "MacroObservation",
    "NewsRecord",
    "ResearchSourceRecord",
]
