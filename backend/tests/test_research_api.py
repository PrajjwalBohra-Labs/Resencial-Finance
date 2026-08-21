from fastapi.testclient import TestClient

from backend.app.api.routes.research import get_research_orchestrator
from backend.app.domain.analytical_finding import (
    AnalyticalConfidence,
    AnalyticalDirection,
    AnalyticalFinding,
    AnalyticalFindingCategory,
)
from backend.app.domain.research import ResearchAnswer
from backend.app.main import app


class FakeResearchOrchestrator:
    def __init__(self) -> None:
        self.requests = []

    async def research(self, request):
        self.requests.append(request)

        return ResearchAnswer(
            question=request.question,
            answer="Research completed.",
            model="test-model",
            provider="fake_llm",
            evidence_count=1,
            analytical_findings=[
                AnalyticalFinding(
                    finding="HDFC Bank outperformed the benchmark.",
                    category=AnalyticalFindingCategory.RELATIONSHIP,
                    metric="HDFC Bank relative performance",
                    value=5.0,
                    unit="percentage_points",
                    direction=AnalyticalDirection.POSITIVE,
                    confidence=AnalyticalConfidence.HIGH,
                    significance="Measures asset performance relative to the benchmark.",
                    methodology="Aligned start-to-end return comparison.",
                    evidence_refs=[
                        "market:HDFCBANK",
                        "benchmark:^NSEI",
                    ],
                    uncertainty="Historical relative performance does not establish future performance.",
                    known=["Observed relative performance: 5.0 percentage points."],
                    unknown=["Future relative performance."],
                )
            ],
        )


def test_research_endpoint() -> None:
    fake = FakeResearchOrchestrator()

    app.dependency_overrides[get_research_orchestrator] = (
        lambda: fake
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/api/research",
            json={
                "question": "Analyse HDFC Bank.",
                "symbols": ["HDFCBANK"],
                "exchange": "NSE",
                "focus": "market",
                "start_date": "2026-08-10",
                "end_date": "2026-08-11",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["question"] == "Analyse HDFC Bank."
        assert body["answer"] == "Research completed."
        assert body["model"] == "test-model"
        assert body["provider"] == "fake_llm"
        assert body["evidence_count"] == 1
        assert "evidence" in body
        assert len(body["evidence"]) == 0

        assert "analytical_findings" in body
        assert len(body["analytical_findings"]) == 1

        finding = body["analytical_findings"][0]

        assert finding["category"] == "relationship"
        assert finding["metric"] == "HDFC Bank relative performance"
        assert finding["value"] == 5.0
        assert finding["unit"] == "percentage_points"
        assert finding["direction"] == "positive"
        assert finding["confidence"] == "high"
        assert finding["evidence_refs"] == [
            "market:HDFCBANK",
            "benchmark:^NSEI",
        ]

        assert len(fake.requests) == 1
        assert fake.requests[0].symbols == ["HDFCBANK"]
        assert fake.requests[0].exchange == "NSE"

    finally:
        app.dependency_overrides.clear()


def test_research_endpoint_rejects_invalid_date_range() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/research",
        json={
            "question": "Analyse HDFC Bank.",
            "symbols": ["HDFCBANK"],
            "exchange": "NSE",
            "start_date": "2026-08-11",
            "end_date": "2026-08-10",
        },
    )

    assert response.status_code == 422

