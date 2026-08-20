from backend.app.domain.analytical_finding import AnalyticalFinding


def format_analytical_findings(
    findings: list[AnalyticalFinding],
) -> str:
    if not findings:
        return "No deterministic analytical findings are available."

    sections: list[str] = []

    for index, finding in enumerate(findings, start=1):
        lines = [
            f"Finding {index}: {finding.finding}",
            f"Category: {finding.category.value}",
            f"Metric: {finding.metric}",
        ]

        if finding.value is not None:
            lines.append(
                f"Value: {finding.value}"
                + (
                    f" {finding.unit}"
                    if finding.unit
                    else ""
                )
            )

        lines.extend(
            [
                f"Direction: {finding.direction.value}",
                f"Confidence: {finding.confidence.value}",
            ]
        )

        if finding.significance:
            lines.append(
                f"Significance: {finding.significance}"
            )

        if finding.methodology:
            lines.append(
                f"Methodology: {finding.methodology}"
            )

        if finding.evidence_refs:
            lines.append(
                "Evidence refs: "
                + ", ".join(finding.evidence_refs)
            )

        if finding.uncertainty:
            lines.append(
                f"Uncertainty: {finding.uncertainty}"
            )

        if finding.known:
            lines.append(
                "Known: " + " | ".join(finding.known)
            )

        if finding.unknown:
            lines.append(
                "Unknown: " + " | ".join(finding.unknown)
            )

        sections.append("\n".join(lines))

    return "\n\n".join(sections)
