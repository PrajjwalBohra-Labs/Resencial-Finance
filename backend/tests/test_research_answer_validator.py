from datetime import datetime, timezone

from backend.app.domain.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceType,
)
from backend.app.domain.research import (
    ResearchContext,
    ResearchRequest,
)
from backend.app.domain.research_validation import (
    ResearchValidationStatus,
)
from backend.app.services.research_answer_validator import (
    ResearchAnswerValidator,
)


def create_context() -> ResearchContext:
    return ResearchContext(
        request=ResearchRequest(
            question="Analyse HDFC Bank.",
            symbols=["HDFCBANK"],
            exchange="NSE",
        ),
        evidence=[
            Evidence(
                evidence_type=EvidenceType.MARKET_DATA,
                title="HDFC Bank market data",
                content=(
                    "Daily open-to-close changes:\n"
                    "2026-08-10: change=-0.5; "
                    "change_percentage=-0.0683526999316473%\n"
                    "2026-08-11: change=-1.5; "
                    "change_percentage=-0.20533880903490762%"
                ),
                source=EvidenceSource(
                    name="Yahoo Finance",
                    provider="yahoo_finance",
                    retrieved_at=datetime.now(timezone.utc),
                ),
            )
        ],
    )


def test_validator_accepts_authoritative_daily_percentage() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_context(),
        answer=(
            "On 2026-08-10, the daily change was -0.07%."
        ),
    )

    assert result.status == ResearchValidationStatus.PASSED
    assert result.issues == []


def test_validator_rejects_conflicting_iso_daily_percentage() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_context(),
        answer=(
            "On 2026-08-10, the stock declined by 0.5%."
        ),
    )

    assert result.status == ResearchValidationStatus.FAILED
    assert len(result.issues) == 1
    assert result.issues[0].code == "daily_percentage_conflict"


def test_validator_rejects_conflicting_human_date_percentage() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_context(),
        answer=(
            "On August 10, the stock declined by 0.5%."
        ),
    )

    assert result.status == ResearchValidationStatus.FAILED
    assert len(result.issues) == 1
    assert result.issues[0].code == "daily_percentage_conflict"


def test_validator_accepts_rounded_human_date_percentage() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_context(),
        answer=(
            "On August 10, the stock declined by 0.07%."
        ),
    )

    assert result.status == ResearchValidationStatus.PASSED


def test_validator_ignores_dates_without_reported_percentages() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_context(),
        answer=(
            "On August 10, the stock declined slightly."
        ),
    )

    assert result.status == ResearchValidationStatus.PASSED


def test_validator_rejects_unsupported_causal_claim() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_context(),
        answer=(
            "The decline may be due to various market and economic factors."
        ),
    )

    assert result.status == ResearchValidationStatus.FAILED
    assert len(result.issues) == 1
    assert result.issues[0].code == "unsupported_causal_claim"


def test_validator_accepts_evidence_limited_interpretation() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_context(),
        answer=(
            "The supplied evidence does not identify the cause of the decline."
        ),
    )

    assert result.status == ResearchValidationStatus.PASSED


def test_validator_accepts_empty_answer() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_context(),
        answer="",
    )

    assert result.status == ResearchValidationStatus.PASSED

def test_validator_matches_each_date_to_the_nearest_percentage() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_context(),
        answer=(
            "August 10 declined by 0.07%, and "
            "August 11 declined by 0.21%."
        ),
    )

    assert result.status == ResearchValidationStatus.PASSED
    assert result.issues == []
