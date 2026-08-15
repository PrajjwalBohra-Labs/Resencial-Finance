from backend.app.domain.research import ResearchContext


class ResearchPromptBuilder:
    """Builds deterministic prompts from an ephemeral research context."""

    def build(
        self,
        context: ResearchContext,
    ) -> tuple[str, str]:
        system_prompt = """
You are Resencial Finance, an Indian financial research assistant.

Your role is research and analysis, not trading execution or personalised
investment advice.

Use the supplied research evidence as the factual basis for your response.

Rules:
1. Do not invent financial facts, prices, dates, financial metrics, news,
   filings, or sources.
2. Clearly distinguish observed facts from interpretation.
3. If the supplied evidence is insufficient to answer something, explicitly
   say that the evidence is insufficient.
4. Do not claim that you accessed information that is not present in the
   supplied evidence.
5. When numerical data is supplied, preserve the numbers accurately.
6. Explain calculations and conclusions rather than merely listing them.
7. For comparisons, compare the available evidence on equivalent dimensions.
8. Focus on Indian financial instruments and the Indian financial context.
9. Do not provide buy, sell, entry, exit, or trading instructions.
10. Produce a thorough research response with clear sections.

Preferred response structure when applicable:
- Executive Summary
- What the Evidence Shows
- Key Observations
- Quantitative Analysis
- Risks / Limitations
- Interpretation
- What Additional Evidence Would Improve the Research

Do not manufacture a section merely to satisfy the structure. Use only sections
that are relevant to the question and available evidence.
""".strip()

        evidence_blocks: list[str] = []

        for index, evidence in enumerate(context.evidence, start=1):
            source = evidence.source

            source_details = [
                f"source_name={source.name}",
                f"provider={source.provider}",
                f"retrieved_at={source.retrieved_at.isoformat()}",
            ]

            if source.url:
                source_details.append(f"url={source.url}")

            if evidence.symbol:
                source_details.append(f"symbol={evidence.symbol}")

            if evidence.exchange:
                source_details.append(f"exchange={evidence.exchange}")

            evidence_blocks.append(
                "\n".join(
                    [
                        f"--- Evidence {index} ---",
                        f"type={evidence.evidence_type.value}",
                        f"title={evidence.title}",
                        *source_details,
                        f"confidence={evidence.confidence}",
                        "content:",
                        evidence.content,
                        f"--- End Evidence {index} ---",
                    ]
                )
            )

        if evidence_blocks:
            evidence_text = "\n\n".join(evidence_blocks)
        else:
            evidence_text = "No research evidence is currently available."

        user_prompt = "\n".join(
            [
                "Research question:",
                context.request.question,
                "",
                f"Research focus: {context.request.focus.value}",
                "",
                "Requested symbols:",
                ", ".join(context.request.symbols)
                if context.request.symbols
                else "None specified",
                "",
                "Research evidence:",
                evidence_text,
                "",
                "Using only the evidence supplied above, produce a thorough "
                "research response to the user's question.",
            ]
        )

        return system_prompt, user_prompt
