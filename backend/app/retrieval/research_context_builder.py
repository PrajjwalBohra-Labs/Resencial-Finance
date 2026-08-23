from backend.app.domain.evidence import Evidence
from backend.app.domain.research import ResearchContext
from backend.app.retrieval.models import RetrievalQuery
from backend.app.retrieval.retriever import EvidenceRetriever


class ResearchContextBuilder:
    """Builds bounded research context from ranked evidence."""

    DEFAULT_MAX_CHARS = 24000

    def __init__(
        self,
        retriever: EvidenceRetriever,
        *,
        max_chars: int = DEFAULT_MAX_CHARS,
    ) -> None:
        if max_chars <= 0:
            raise ValueError("max_chars must be greater than zero.")

        self._retriever = retriever
        self._max_chars = max_chars

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

    @classmethod
    def _index_evidence(
        cls,
        evidence: list[Evidence],
    ) -> dict[str, Evidence]:
        return {
            cls._evidence_id(item, index): item
            for index, item in enumerate(evidence)
        }

    @staticmethod
    def _deduplicate(
        evidence: list[Evidence],
    ) -> list[Evidence]:
        seen: set[tuple[object, ...]] = set()
        result: list[Evidence] = []

        for item in evidence:
            key = (
                item.evidence_type.value,
                item.symbol,
                item.exchange,
                item.title,
                item.content,
                item.source.name,
                item.source.provider,
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(item)

        return result

    @staticmethod
    def _render_evidence(
        evidence: list[Evidence],
    ) -> str:
        sections: list[str] = []

        for index, item in enumerate(evidence, start=1):
            source = item.source

            sections.append(
                "\n".join(
                    [
                        f"[Evidence {index}]",
                        f"Type: {item.evidence_type.value}",
                        f"Title: {item.title}",
                        f"Symbol: {item.symbol or 'N/A'}",
                        f"Exchange: {item.exchange or 'N/A'}",
                        f"Provider: {source.provider}",
                        f"Source: {source.name}",
                        f"Retrieved at: {source.retrieved_at.isoformat()}",
                        f"Confidence: {item.confidence}",
                        "",
                        item.content.strip(),
                    ]
                )
            )

        return "\n\n".join(sections)

    def _apply_budget(
        self,
        evidence: list[Evidence],
    ) -> list[Evidence]:
        selected: list[Evidence] = []

        for item in evidence:
            candidate = selected + [item]

            if len(self._render_evidence(candidate)) > self._max_chars:
                break

            selected.append(item)

        return selected

    async def build(
        self,
        query: RetrievalQuery,
        evidence: list[Evidence],
        *,
        contextual_evidence: list[Evidence] | None = None,
    ) -> ResearchContext:
        if not evidence:
            return ResearchContext(
                request=self._request_from_query(query),
                evidence=[],
            )

        evidence_by_id = self._index_evidence(evidence)

        result = await self._retriever.retrieve(
            query,
            evidence,
        )

        ranked: list[Evidence] = []

        for chunk in result.chunks:
            item = evidence_by_id.get(chunk.evidence_id)

            if item is not None:
                ranked.append(item)

        ranked = self._deduplicate(ranked)

        if contextual_evidence:
            ranked_keys = {
                (
                    item.evidence_type,
                    item.symbol,
                    item.exchange,
                    item.title,
                    item.content,
                )
                for item in ranked
            }

            contextual = [
                item
                for item in contextual_evidence
                if (
                    item.evidence_type,
                    item.symbol,
                    item.exchange,
                    item.title,
                    item.content,
                )
                not in ranked_keys
            ]

            ranked.extend(
                self._deduplicate(contextual)
            )

        ranked = self._apply_budget(ranked)

        context = ResearchContext(
            request=self._request_from_query(query),
            evidence=ranked,
        )

        return context

    @staticmethod
    def _request_from_query(
        query: RetrievalQuery,
    ):
        from backend.app.domain.research import ResearchRequest

        return ResearchRequest(
            question=query.question,
            symbols=list(query.symbols),
            exchange=query.exchange,
            start_date=query.start_date,
            end_date=query.end_date,
        )
