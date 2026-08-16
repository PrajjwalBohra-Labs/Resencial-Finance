from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ResearchValidationStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"


class ResearchValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    severity: str = "error"


class ResearchValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ResearchValidationStatus
    issues: list[ResearchValidationIssue] = Field(
        default_factory=list,
    )

    @property
    def passed(self) -> bool:
        return self.status == ResearchValidationStatus.PASSED
