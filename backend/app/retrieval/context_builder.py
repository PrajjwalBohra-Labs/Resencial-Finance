from __future__ import annotations

from backend.app.retrieval.models import RetrievalResult


class ResearchContextBuilder:
    """
    Converts retrieved evidence into a bounded LLM context.

    Financial values are copied verbatim from retrieved evidence.
    This layer does not interpret or recompute them.
    """

    def build(
        self,
        result: RetrievalResult,
    ) -> str:
        if not result.chunks:
            return (
                "RESEARCH EVIDENCE\n"
                "No relevant evidence was retrieved."
            )

        sections = [
            "RESEARCH EVIDENCE",
            "",
            "Use the following evidence as the factual basis "
            "for the research answer.",
            "Do not invent facts that are absent from the evidence.",
            "",
        ]

        for index, chunk in enumerate(
            result.chunks,
            start=1,
        ):
            sections.extend(
                [
                    f"[Evidence {index}]",
                    f"Evidence ID: {chunk.evidence_id}",
                    f"Type: {chunk.evidence_type.value}",
                    f"Symbol: {chunk.symbol or 'unknown'}",
                    f"Exchange: {chunk.exchange or 'unknown'}",
                    (
                        "Observation date: "
                        f"{chunk.observation_date or 'unknown'}"
                    ),
                    f"Source: {chunk.source}",
                    f"Provider: {chunk.provider or 'unknown'}",
                    "",
                    chunk.text,
                    "",
                ]
            )

        sections.extend(
            [
                "RESEARCH INSTRUCTIONS",
                "",
                "1. Treat retrieved evidence as the factual basis.",
                "2. Preserve reported numerical values.",
                "3. Distinguish evidence from interpretation.",
                "4. Do not infer causality unless evidence supports it.",
                "5. Identify missing evidence explicitly.",
                "6. Cite the relevant Evidence ID when making "
                "evidence-dependent claims.",
            ]
        )

        return "\n".join(sections)
