from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AnalyticalFindingCategory(StrEnum):
    GROWTH = "growth"
    TREND = "trend"
    DISTRIBUTION = "distribution"
    RELATIONSHIP = "relationship"
    ANOMALY = "anomaly"
    RISK = "risk"
    QUALITY = "quality"


class AnalyticalDirection(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class AnalyticalConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AnalyticalFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding: str = Field(min_length=1)
    category: AnalyticalFindingCategory
    metric: str = Field(min_length=1)

    value: float | None = None
    unit: str | None = None

    direction: AnalyticalDirection = AnalyticalDirection.NEUTRAL
    confidence: AnalyticalConfidence = AnalyticalConfidence.MEDIUM

    significance: str | None = None
    methodology: str | None = None

    evidence_refs: list[str] = Field(default_factory=list)

    uncertainty: str | None = None
    known: list[str] = Field(default_factory=list)
    unknown: list[str] = Field(default_factory=list)
