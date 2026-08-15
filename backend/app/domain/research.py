from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain.evidence import Evidence


class ResearchFocus(StrEnum):
    GENERAL = "general"
    FUNDAMENTAL = "fundamental"
    VALUATION = "valuation"
    RISK = "risk"
    MARKET = "market"
    FIXED_INCOME = "fixed_income"
    MACRO = "macro"
    COMPARISON = "comparison"


class ResearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    symbols: list[str] = Field(default_factory=list)
    exchange: str | None = None
    focus: ResearchFocus = ResearchFocus.GENERAL


class ResearchContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: ResearchRequest
    evidence: list[Evidence] = Field(default_factory=list)

    def add_evidence(self, item: Evidence) -> None:
        self.evidence.append(item)
