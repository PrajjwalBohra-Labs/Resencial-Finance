from __future__ import annotations

import math
import re
from datetime import date
from typing import Sequence

from backend.app.domain.evidence import Evidence
from backend.app.retrieval.models import (
    EvidenceChunk,
    RetrievalQuery,
    RetrievalResult,
)


class EvidenceRetriever:
    """
    Deterministic hybrid evidence retriever.

    The retriever selects and ranks evidence only. It never changes,
    recalculates, summarizes, or interprets financial values.
    """

    _TOKEN_RE = re.compile(
        r"[A-Za-z0-9][A-Za-z0-9._%/-]*"
    )

    _STOPWORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "based",
        "by",
        "for",
        "from",
        "how",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "was",
        "what",
        "with",
    }

    async def retrieve(
        self,
        query: RetrievalQuery,
        evidence: Sequence[Evidence],
    ) -> RetrievalResult:
        ranked: list[EvidenceChunk] = []

        query_tokens = self._tokens(query.question)
        symbols = query.normalized_symbols()
        exchange = query.normalized_exchange()

        for index, item in enumerate(evidence):
            if not self._matches_metadata(
                item=item,
                query=query,
            ):
                continue

            lexical_score = self._lexical_score(
                query_tokens=query_tokens,
                evidence=item,
            )

            metadata_score = self._metadata_score(
                item=item,
                query=query,
                symbols=symbols,
                exchange=exchange,
            )

            temporal_score = self._temporal_score(
                item=item,
                query=query,
            )

            if (
                lexical_score <= 0
                and metadata_score <= 0
                and temporal_score <= 0
            ):
                continue

            total_score = (
                lexical_score * 0.50
                + metadata_score * 0.30
                + temporal_score * 0.20
            )

            ranked.append(
                EvidenceChunk(
                    evidence_id=self._evidence_id(
                        item,
                        index,
                    ),
                    text=item.content,
                    symbol=item.symbol,
                    exchange=item.exchange,
                    evidence_type=item.evidence_type,
                    observation_date=self._observation_date(item),
                    published_at=item.source.published_at,
                    retrieved_at=item.source.retrieved_at,
                    source=item.source.name,
                    provider=item.source.provider,
                    lexical_score=lexical_score,
                    metadata_score=metadata_score,
                    temporal_score=temporal_score,
                    total_score=total_score,
                )
            )

        ranked.sort(
            key=lambda chunk: (
                -chunk.total_score,
                -chunk.temporal_score,
                -chunk.metadata_score,
                -chunk.lexical_score,
                chunk.evidence_id,
            )
        )

        return RetrievalResult(
            query=query,
            chunks=ranked[: query.limit],
        )

    @classmethod
    def _tokens(cls, text: str) -> set[str]:
        tokens = {
            token.lower()
            for token in cls._TOKEN_RE.findall(text)
        }

        return {
            token
            for token in tokens
            if token not in cls._STOPWORDS
        }

    @classmethod
    def _lexical_score(
        cls,
        *,
        query_tokens: set[str],
        evidence: Evidence,
    ) -> float:
        if not query_tokens:
            return 0.0

        evidence_tokens = cls._tokens(
            " ".join(
                [
                    evidence.title,
                    evidence.content,
                    evidence.symbol or "",
                    evidence.exchange or "",
                    evidence.source.name,
                ]
            )
        )

        overlap = query_tokens & evidence_tokens

        if not overlap:
            return 0.0

        weighted_overlap = sum(
            1.0 / math.sqrt(1.0 + len(token))
            for token in overlap
        )

        weighted_query = sum(
            1.0 / math.sqrt(1.0 + len(token))
            for token in query_tokens
        )

        if weighted_query == 0:
            return 0.0

        return min(
            1.0,
            weighted_overlap / weighted_query,
        )

    @classmethod
    def _matches_metadata(
        cls,
        *,
        item: Evidence,
        query: RetrievalQuery,
    ) -> bool:
        symbols = query.normalized_symbols()
        exchange = query.normalized_exchange()

        if symbols:
            if item.symbol is None:
                return False

            if item.symbol.upper() not in symbols:
                return False

        if exchange:
            if item.exchange is None:
                return False

            if item.exchange.upper() != exchange:
                return False

        if (
            query.evidence_types
            and item.evidence_type
            not in query.evidence_types
        ):
            return False

        observation_date = cls._observation_date(item)

        if query.start_date and observation_date:
            if observation_date < query.start_date:
                return False

        if query.end_date and observation_date:
            if observation_date > query.end_date:
                return False

        return True

    @classmethod
    def _metadata_score(
        cls,
        *,
        item: Evidence,
        query: RetrievalQuery,
        symbols: set[str],
        exchange: str | None,
    ) -> float:
        score = 0.0

        if symbols and item.symbol:
            if item.symbol.upper() in symbols:
                score += 0.55

        if exchange and item.exchange:
            if item.exchange.upper() == exchange:
                score += 0.20

        if (
            query.evidence_types
            and item.evidence_type in query.evidence_types
        ):
            score += 0.20

        return min(1.0, score)

    @classmethod
    def _temporal_score(
        cls,
        *,
        item: Evidence,
        query: RetrievalQuery,
    ) -> float:
        observation_date = cls._observation_date(item)

        if observation_date is None:
            return 0.0

        if query.start_date and query.end_date:
            if (
                query.start_date
                <= observation_date
                <= query.end_date
            ):
                return 1.0

            distance = min(
                abs(
                    observation_date
                    - query.start_date
                ).days,
                abs(
                    observation_date
                    - query.end_date
                ).days,
            )

            return max(
                0.0,
                1.0 / (1.0 + distance / 30.0),
            )

        if query.start_date:
            distance = abs(
                observation_date
                - query.start_date
            ).days

            return max(
                0.0,
                1.0 / (1.0 + distance / 30.0),
            )

        if query.end_date:
            distance = abs(
                observation_date
                - query.end_date
            ).days

            return max(
                0.0,
                1.0 / (1.0 + distance / 30.0),
            )

        return 0.0

    @staticmethod
    def _observation_date(
        evidence: Evidence,
    ) -> date | None:
        match = re.search(
            r"\b(20\d{2}-\d{2}-\d{2})\b",
            evidence.content,
        )

        if not match:
            return None

        try:
            return date.fromisoformat(
                match.group(1)
            )
        except ValueError:
            return None

    @staticmethod
    def _evidence_id(
        evidence: Evidence,
        index: int,
    ) -> str:
        symbol = evidence.symbol or "unknown"
        exchange = evidence.exchange or "unknown"

        return (
            f"{evidence.evidence_type.value}:"
            f"{symbol.upper()}:"
            f"{exchange.upper()}:"
            f"{index}"
        )

