from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class EvidenceType(StrEnum):
    MARKET_DATA = "market_data"
    FUNDAMENTAL = "fundamental"
    NEWS = "news"
    FILING = "filing"
    REGULATORY = "regulatory"
    MACRO = "macro"


class EvidenceSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    url: str | None = None
    published_at: datetime | None = None
    retrieved_at: datetime
    provider: str


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_type: EvidenceType
    title: str
    content: str
    source: EvidenceSource

    symbol: str | None = None
    exchange: str | None = None

    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
