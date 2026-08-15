from fastapi.testclient import TestClient

from backend.app.api.routes.research import get_research_orchestrator
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
