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

def create_fundamental_context() -> ResearchContext:
    return ResearchContext(
        request=ResearchRequest(
            question="Analyse HDFC Bank fundamentals.",
            symbols=["HDFCBANK"],
            exchange="NSE",
        ),
        evidence=[
            Evidence(
                evidence_type=EvidenceType.FUNDAMENTAL,
                title="HDFC Bank fundamental data",
                content=(
                    "Fundamental evidence:\n"
                    "Currency: INR\n\n"
                    "Latest income statement:\n"
                    "Period: 2026-03-31\n"
                    "Total Revenue: 1925667800000.0\n"
                    "Net Income: 704793400000.0\n"
                    "Basic EPS: 45.89\n"
                    "Diluted EPS: 45.75\n\n"
                    "Key ratios:\n"
                    "Trailing P/E: 15.89766\n"
                    "Forward P/E: 11.613419\n"
                    "Price/book: 1.8460538\n"
                    "Return on equity: 13.838%\n"
                    "Return on assets: 1.75%\n"
                    "Revenue growth: 16.6%\n"
                    "Earnings growth: 18.1%"
                ),
                source=EvidenceSource(
                    name="Yahoo Finance",
                    provider="yahoo_finance",
                    retrieved_at=datetime.now(timezone.utc),
                ),
                symbol="HDFCBANK",
                exchange="NSE",
            )
        ],
    )


def test_validator_accepts_rounded_fundamental_numbers() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_fundamental_context(),
        answer=(
            "Trailing P/E was 15.9, P/B was 1.85, "
            "ROE was 13.8%, and revenue growth was 16.6%."
        ),
    )

    assert result.status == ResearchValidationStatus.PASSED


def test_validator_rejects_conflicting_fundamental_number() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_fundamental_context(),
        answer=(
            "The trailing P/E was 25.4."
        ),
    )

    assert result.status == ResearchValidationStatus.FAILED
    assert any(
        issue.code == "fundamental_number_conflict"
        for issue in result.issues
    )


def test_validator_rejects_unsupported_valuation_claim() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_fundamental_context(),
        answer=(
            "The company's P/E of 15.9 suggests that it is currently "
            "overvalued."
        ),
    )

    assert result.status == ResearchValidationStatus.FAILED
    assert any(
        issue.code == "unsupported_valuation_claim"
        for issue in result.issues
    )


def test_validator_accepts_neutral_valuation_statement() -> None:
    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=create_fundamental_context(),
        answer=(
            "The trailing P/E is 15.9 and the price-to-book ratio is 1.85. "
            "The supplied evidence does not include peer or benchmark "
            "valuation data."
        ),
    )

    assert result.status == ResearchValidationStatus.PASSED

def test_validator_accepts_dividend_yield_percentage() -> None:
    context = create_fundamental_context()

    context.evidence[0].content += (
        "\nDividend yield: 1.79%"
    )

    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=context,
        answer="Dividend yield was 1.79%."
    )

    assert result.status == ResearchValidationStatus.PASSED


def test_validator_rejects_conflicting_dividend_yield() -> None:
    context = create_fundamental_context()

    context.evidence[0].content += (
        "\nDividend yield: 1.79%"
    )

    validator = ResearchAnswerValidator()

    result = validator.validate(
        context=context,
        answer="Dividend yield was 179%."
    )

    assert result.status == ResearchValidationStatus.FAILED

    assert any(
        issue.code == "fundamental_number_conflict"
        for issue in result.issues
    )


def test_validator_supports_mixed_evidence_context() -> None:
    from backend.app.domain.evidence import (
        Evidence,
        EvidenceSource,
        EvidenceType,
    )

    context = create_context()

    context.evidence.extend(
        [
            Evidence(
                evidence_type=EvidenceType.NEWS,
                title="HDFC Bank news",
                content="Company commentary was supplied.",
                source=EvidenceSource(
                    name="Test News",
                    provider="test-news",
                    retrieved_at=datetime.now(timezone.utc),
                ),
                symbol="HDFCBANK",
                exchange="NSE",
            ),
            Evidence(
                evidence_type=EvidenceType.FILING,
                title="HDFC Bank filing",
                content="Regulatory disclosure was supplied.",
                source=EvidenceSource(
                    name="Test Filing",
                    provider="test-filings",
                    retrieved_at=datetime.now(timezone.utc),
                ),
                symbol="HDFCBANK",
                exchange="NSE",
            ),
            Evidence(
                evidence_type=EvidenceType.MACRO,
                title="Repo rate",
                content="Repo rate: 6.5%.",
                source=EvidenceSource(
                    name="Test Macro",
                    provider="test-macro",
                    retrieved_at=datetime.now(timezone.utc),
                ),
            ),
            Evidence(
                evidence_type=EvidenceType.REGULATORY,
                title="Government bond",
                content="Yield: 6.8%.",
                source=EvidenceSource(
                    name="Test Bonds",
                    provider="test-bonds",
                    retrieved_at=datetime.now(timezone.utc),
                ),
            ),
        ]
    )

    result = ResearchAnswerValidator().validate(
        context=context,
        answer=(
            "The supplied evidence includes market observations, "
            "company news, filings, macro observations, and bond data. "
            "The supplied evidence does not establish a causal explanation "
            "for the observed market movement."
        ),
    )

    assert result.status == ResearchValidationStatus.PASSED
    assert result.issues == []
