from backend.app.core.config import Settings
from backend.app.data.providers.in_memory_research import InMemoryResearchProvider
from backend.app.data.providers.news import NewsProvider
from backend.app.data.providers.news_http import HttpNewsProvider


def build_news_provider(
    settings: Settings,
) -> NewsProvider:
    provider_name = settings.news_provider.strip().lower()

    if provider_name == "http_news":
        if not settings.news_api_base_url.strip():
            return InMemoryResearchProvider()

        return HttpNewsProvider(
            base_url=settings.news_api_base_url,
            api_key=settings.news_api_key or None,
        )

    if provider_name == "in_memory":
        return InMemoryResearchProvider()

    raise ValueError(
        f"Unsupported news provider: {settings.news_provider}"
    )
