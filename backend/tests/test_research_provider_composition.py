from backend.app.api.routes.research import get_research_orchestrator
from backend.app.core.config import get_settings
from backend.app.data.providers import (
    HttpNewsProvider,
    InMemoryResearchProvider,
)
from backend.app.services.research_data_assembler import ResearchDataAssembler


def _news_provider_from_orchestrator(
    orchestrator,
):
    assembler = orchestrator._evidence_assembler

    assert isinstance(
        assembler,
        ResearchDataAssembler,
    )

    adapter = assembler._news_evidence_port

    return adapter._provider


def test_research_dependency_uses_in_memory_news_provider_by_default() -> None:
    get_settings.cache_clear()

    try:
        orchestrator = get_research_orchestrator()

        provider = _news_provider_from_orchestrator(
            orchestrator,
        )

        assert isinstance(
            provider,
            InMemoryResearchProvider,
        )
    finally:
        get_settings.cache_clear()


def test_research_dependency_uses_http_news_provider_when_configured(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "NEWS_PROVIDER",
        "http_news",
    )
    monkeypatch.setenv(
        "NEWS_API_BASE_URL",
        "https://news.test",
    )
    monkeypatch.setenv(
        "NEWS_API_KEY",
        "test-key",
    )

    get_settings.cache_clear()

    try:
        orchestrator = get_research_orchestrator()

        provider = _news_provider_from_orchestrator(
            orchestrator,
        )

        assert isinstance(
            provider,
            HttpNewsProvider,
        )

        assert provider._base_url == "https://news.test"
        assert provider._api_key == "test-key"
    finally:
        get_settings.cache_clear()


def test_research_dependency_keeps_other_advanced_providers_composed() -> None:
    get_settings.cache_clear()

    try:
        orchestrator = get_research_orchestrator()

        assembler = orchestrator._evidence_assembler

        assert assembler._filing_evidence_port is not None
        assert assembler._macro_evidence_port is not None
        assert assembler._bond_evidence_port is not None
    finally:
        get_settings.cache_clear()
