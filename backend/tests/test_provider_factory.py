import pytest

from backend.app.core.config import Settings
from backend.app.data.providers import (
    HttpNewsProvider,
    InMemoryResearchProvider,
    build_news_provider,
)


def test_build_news_provider_http() -> None:
    settings = Settings(
        news_provider="http_news",
        news_api_base_url="https://news.test",
        news_api_key="test-key",
    )

    provider = build_news_provider(settings)

    assert isinstance(provider, HttpNewsProvider)


def test_build_news_provider_in_memory() -> None:
    settings = Settings(
        news_provider="in_memory",
    )

    provider = build_news_provider(settings)

    assert isinstance(provider, InMemoryResearchProvider)


def test_http_news_provider_without_url_falls_back_to_in_memory() -> None:
    settings = Settings(
        news_provider="http_news",
        news_api_base_url="",
    )

    provider = build_news_provider(settings)

    assert isinstance(provider, InMemoryResearchProvider)


def test_unknown_news_provider_rejected() -> None:
    settings = Settings(
        news_provider="unknown",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported news provider",
    ):
        build_news_provider(settings)
