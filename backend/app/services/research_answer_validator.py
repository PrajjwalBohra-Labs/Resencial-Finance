import re
from datetime import date

from backend.app.domain.research import ResearchContext
from backend.app.domain.research_validation import (
    ResearchValidationIssue,
    ResearchValidationResult,
    ResearchValidationStatus,
)


class ResearchAnswerValidator:
    """Checks generated research answers against supplied evidence."""

    _DAILY_CHANGE_PATTERN = re.compile(
        r"(?P<date>\d{4}-\d{2}-\d{2}):"
        r"\s*change=(?P<change>-?\d+(?:\.\d+)?);"
        r"\s*change_percentage=(?P<percentage>-?\d+(?:\.\d+)?)%"
    )

    _FUNDAMENTAL_NUMBER_ALIASES = {
        "Trailing P/E": (
            "Trailing P/E",
            "trailing PE",
            "trailing P/E ratio",
        ),
        "Forward P/E": (
            "Forward P/E",
            "forward PE",
            "forward P/E ratio",
        ),
        "Price/book": (
            "Price/book",
            "P/B",
            "P/B ratio",
            "price-to-book",
            "price-to-book ratio",
        ),
        "Return on equity": (
            "Return on equity",
            "ROE",
        ),
        "Return on assets": (
            "Return on assets",
            "ROA",
        ),
        "Profit margin": (
            "Profit margin",
            "profit margins",
        ),
        "Operating margin": (
            "Operating margin",
            "operating margins",
        ),
        "Revenue growth": (
            "Revenue growth",
        ),
        "Earnings growth": (
            "Earnings growth",
        ),
        "Dividend yield": (
            "Dividend yield",
        ),
        "Total Revenue": (
            "Total Revenue",
            "Revenue",
        ),
        "Net Income": (
            "Net Income",
            "net income",
        ),
        "Basic EPS": (
            "Basic EPS",
            "basic EPS",
        ),
        "Diluted EPS": (
            "Diluted EPS",
            "diluted EPS",
        ),
        "Total Assets": (
            "Total Assets",
            "total assets",
        ),
        "Stockholders Equity": (
            "Stockholders Equity",
            "stockholders equity",
            "shareholders equity",
        ),
        "Operating Cash Flow": (
            "Operating Cash Flow",
            "operating cash flow",
        ),
        "Free Cash Flow": (
            "Free Cash Flow",
            "free cash flow",
        ),
    }

    _UNSUPPORTED_VALUATION_PATTERNS = (
        re.compile(
            r"\b(?:is|appears|seems|looks)\s+(?:currently\s+)?"
            r"overvalued\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:is|appears|seems|looks)\s+(?:currently\s+)?"
            r"undervalued\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bsuggests?\s+(?:that\s+)?(?:the\s+company|the\s+stock)"
            r"\s+is\s+(?:currently\s+)?(?:overvalued|undervalued)\b",
            re.IGNORECASE,
        ),
    )

    _CAUSE_PATTERNS = (
        re.compile(r"\bmay be due to\b", re.IGNORECASE),
        re.compile(r"\bcould be due to\b", re.IGNORECASE),
        re.compile(r"\bcaused by\b", re.IGNORECASE),
        re.compile(r"\bthe reason for\b", re.IGNORECASE),
        re.compile(r"\bdriven by\b", re.IGNORECASE),
        re.compile(r"\bdue to various\b", re.IGNORECASE),
    )

    _DECLINE_WORDS = re.compile(
        r"\b(decline|declined|decreased|decrease|fell|fall|down|drop|dropped|loss|lost)\b",
        re.IGNORECASE,
    )

    _RISE_WORDS = re.compile(
        r"\b(increase|increased|rise|rose|rallied|up|gain|gained)\b",
        re.IGNORECASE,
    )

    def validate(
        self,
        *,
        context: ResearchContext,
        answer: str,
    ) -> ResearchValidationResult:
        if not answer:
            return ResearchValidationResult(
                status=ResearchValidationStatus.PASSED,
            )

        issues: list[ResearchValidationIssue] = []

        issues.extend(
            self._validate_daily_percentages(
                context=context,
                answer=answer,
            )
        )

        issues.extend(
            self._validate_fundamental_numbers(
                context=context,
                answer=answer,
            )
        )

        if self._contains_unsupported_causal_claim(answer):
            issues.append(
                ResearchValidationIssue(
                    code="unsupported_causal_claim",
                    message=(
                        "The generated answer attributes the market or "
                        "financial movement to a cause that is not established "
                        "by the supplied evidence."
                    ),
                )
            )

        if self._contains_unsupported_valuation_claim(answer):
            issues.append(
                ResearchValidationIssue(
                    code="unsupported_valuation_claim",
                    message=(
                        "The generated answer makes an overvaluation or "
                        "undervaluation conclusion without comparative or "
                        "valuation evidence establishing that conclusion."
                    ),
                )
            )

        if issues:
            return ResearchValidationResult(
                status=ResearchValidationStatus.FAILED,
                issues=issues,
            )

        return ResearchValidationResult(
            status=ResearchValidationStatus.PASSED,
        )

    def _validate_daily_percentages(
        self,
        *,
        context: ResearchContext,
        answer: str,
    ) -> list[ResearchValidationIssue]:
        issues: list[ResearchValidationIssue] = []

        expected_daily_changes = self._extract_daily_changes(
            context
        )

        for observation_date, expected_percentage in (
            expected_daily_changes.items()
        ):
            reported = self._find_reported_percentage_for_date(
                answer=answer,
                observation_date=observation_date,
            )

            if reported is None:
                continue

            reported_percentage, nearby_text = reported

            if not self._percentages_match(
                expected=expected_percentage,
                reported=reported_percentage,
                context=nearby_text,
            ):
                issues.append(
                    ResearchValidationIssue(
                        code="daily_percentage_conflict",
                        message=(
                            f"Generated answer reports "
                            f"{reported_percentage}% for "
                            f"{observation_date}, but the authoritative "
                            f"backend value is {expected_percentage}%."
                        ),
                    )
                )

        return issues

    def _validate_fundamental_numbers(
        self,
        *,
        context: ResearchContext,
        answer: str,
    ) -> list[ResearchValidationIssue]:
        issues: list[ResearchValidationIssue] = []

        for evidence in context.evidence:
            if evidence.evidence_type.value != "fundamental":
                continue

            authoritative = self._extract_fundamental_numbers(
                evidence.content
            )

            for label, expected in authoritative.items():
                reported = self._find_reported_fundamental_number(
                    answer=answer,
                    label=label,
                )

                if reported is None:
                    continue

                if not self._numbers_match(
                    expected=expected,
                    reported=reported,
                    label=label,
                ):
                    issues.append(
                        ResearchValidationIssue(
                            code="fundamental_number_conflict",
                            message=(
                                f"Generated answer reports {reported} "
                                f"for {label}, but the authoritative "
                                f"backend value is {expected}."
                            ),
                        )
                    )

        return issues

    @classmethod
    def _extract_fundamental_numbers(
        cls,
        content: str,
    ) -> dict[str, float]:
        values: dict[str, float] = {}

        for label, aliases in cls._FUNDAMENTAL_NUMBER_ALIASES.items():
            for alias in aliases:
                match = re.search(
                    rf"^{re.escape(alias)}:\s*"
                    rf"(-?\d+(?:\.\d+)?)%?$",
                    content,
                    flags=re.IGNORECASE | re.MULTILINE,
                )

                if match is not None:
                    values[label] = float(match.group(1))
                    break

        return values

    @classmethod
    def _find_reported_fundamental_number(
        cls,
        *,
        answer: str,
        label: str,
    ) -> float | None:
        aliases = cls._FUNDAMENTAL_NUMBER_ALIASES.get(
            label,
            (label,),
        )

        for alias in aliases:
            match = re.search(
                rf"(?<!\w){re.escape(alias)}(?!\w)"
                rf"[\s:=-]*"
                rf"(?:is|was|of)?"
                rf"[\s:=-]*"
                rf"(-?\d+(?:\.\d+)?)%?",
                answer,
                flags=re.IGNORECASE,
            )

            if match is not None:
                return float(match.group(1))

        return None

    @staticmethod
    def _numbers_match(
        *,
        expected: float,
        reported: float,
        label: str,
    ) -> bool:
        # Allow ordinary display rounding while rejecting material
        # differences. Larger financial quantities need relative tolerance;
        # small ratios need a modest absolute floor.
        tolerance = max(
            abs(expected) * 0.01,
            0.01 if abs(expected) < 100 else abs(expected) * 0.001,
        )

        return abs(expected - reported) <= tolerance

    @classmethod
    def _extract_daily_changes(
        cls,
        context: ResearchContext,
    ) -> dict[str, float]:
        values: dict[str, float] = {}

        for evidence in context.evidence:
            for match in cls._DAILY_CHANGE_PATTERN.finditer(
                evidence.content
            ):
                values[match.group("date")] = float(
                    match.group("percentage")
                )

        return values

    @staticmethod
    def _date_aliases(
        observation_date: str,
    ) -> tuple[str, ...]:
        parsed = date.fromisoformat(observation_date)

        return (
            parsed.isoformat(),
            f"{parsed.strftime('%B')} {parsed.day}",
            f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}",
            f"{parsed.month}/{parsed.day}/{parsed.year}",
        )

    @classmethod
    def _find_reported_percentage_for_date(
        cls,
        *,
        answer: str,
        observation_date: str,
    ) -> tuple[float, str] | None:
        aliases = cls._date_aliases(observation_date)

        sentences = re.split(
            r"(?<=[.!?])\s+|\n+",
            answer,
        )

        for sentence in sentences:
            for alias in aliases:
                alias_matches = list(
                    re.finditer(
                        re.escape(alias),
                        sentence,
                        flags=re.IGNORECASE,
                    )
                )

                if not alias_matches:
                    continue

                percentage_matches = list(
                    re.finditer(
                        r"-?\d+(?:\.\d+)?%",
                        sentence,
                    )
                )

                if not percentage_matches:
                    continue

                for alias_match in alias_matches:
                    nearest = min(
                        percentage_matches,
                        key=lambda match: abs(
                            match.start() - alias_match.end()
                        ),
                    )

                    if (
                        abs(
                            nearest.start()
                            - alias_match.end()
                        )
                        <= 120
                    ):
                        context_start = max(
                            0,
                            alias_match.start() - 40,
                        )
                        context_end = min(
                            len(sentence),
                            nearest.end() + 40,
                        )

                        return (
                            float(
                                nearest.group(0).rstrip("%")
                            ),
                            sentence[
                                context_start:context_end
                            ],
                        )

        return None

    @classmethod
    def _contains_unsupported_causal_claim(
        cls,
        answer: str,
    ) -> bool:
        return any(
            pattern.search(answer)
            for pattern in cls._CAUSE_PATTERNS
        )

    @classmethod
    def _contains_unsupported_valuation_claim(
        cls,
        answer: str,
    ) -> bool:
        return any(
            pattern.search(answer)
            for pattern in cls._UNSUPPORTED_VALUATION_PATTERNS
        )

    @classmethod
    def _percentages_match(
        cls,
        *,
        expected: float,
        reported: float,
        context: str,
    ) -> bool:
        tolerance = max(
            0.01,
            abs(expected) * 0.05,
        )

        if abs(abs(expected) - abs(reported)) > tolerance:
            return False

        if expected < 0 and reported > 0:
            return bool(cls._DECLINE_WORDS.search(context))

        if expected > 0 and reported < 0:
            return bool(cls._RISE_WORDS.search(context))

        return True

