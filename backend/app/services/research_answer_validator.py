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

        if self._contains_unsupported_causal_claim(answer):
            issues.append(
                ResearchValidationIssue(
                    code="unsupported_causal_claim",
                    message=(
                        "The generated answer attributes the market "
                        "movement to a cause that is not established by "
                        "the supplied evidence."
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

                    # Only associate a percentage that is reasonably close
                    # to the date in the same sentence.
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
