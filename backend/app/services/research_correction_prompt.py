from backend.app.domain.research_validation import ResearchValidationResult


def build_correction_prompt(
    *,
    original_prompt: str,
    validation: ResearchValidationResult,
) -> str:
    issues = "\n".join(
        f"- [{issue.code}] {issue.message}"
        for issue in validation.issues
    )

    return "\n".join(
        [
            original_prompt,
            "",
            "IMPORTANT: Your previous answer failed backend validation.",
            "Correct the answer before returning it.",
            "",
            "Validation issues:",
            issues,
            "",
            "Use only the supplied evidence.",
            "Do not invent facts, causes, or financial metrics.",
            "Copy authoritative backend-calculated values accurately.",
            "If the evidence is insufficient, say so explicitly.",
            "Return only the corrected research answer.",
        ]
    )
