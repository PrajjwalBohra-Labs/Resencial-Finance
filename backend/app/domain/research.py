from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.domain.evidence import Evidence
from backend.app.domain.llm import LLMUsage
from backend.app.domain.research_validation import ResearchValidationResult, ResearchValidationStatus


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
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> "ResearchRequest":
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError(
                "start_date must be before or equal to end_date."
            )

        return self


class ResearchContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: ResearchRequest
    evidence: list[Evidence] = Field(default_factory=list)

    def add_evidence(self, item: Evidence) -> None:
        self.evidence.append(item)


class ResearchAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    answer: str
    model: str
    provider: str
    evidence_count: int = Field(ge=0)
    evidence: list[Evidence] = Field(default_factory=list)
    usage: LLMUsage = Field(default_factory=LLMUsage)
    validation: ResearchValidationResult = Field(
        default_factory=lambda: ResearchValidationResult(
            status=ResearchValidationStatus.PASSED
        )
    )


