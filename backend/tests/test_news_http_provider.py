from datetime import date, datetime, timezone

import httpx
import pytest

from backend.app.core.exceptions import (
    DataProviderResponseError,
    DataProviderUnavailableError,
)
from backend.app.data.providers.news_http import HttpNewsProvider


def make_client(
    handler,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://news.test",
    )


@pytest.mark.asyncio
async def test_provider_name() -> None:
    provider = HttpNewsProvider(
        base_url="https://news.test",
        client=make_client(
            lambda request: httpx.Response(
                200,
                json={"articles": []},
            )
        ),
    )

    assert provider.name == "http_news"


@pytest.mark.asyncio
async def test_search_news_normalizes_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/search"
        assert request.url.params["query"] == "HDFC Bank"
        assert request.url.params["start_date"] == "2026-08-10"
        assert request.url.params["end_date"] == "2026-08-11"

        return httpx.Response(
            200,
            json={
                "articles": [
                    {
                        "title": "HDFC Bank earnings",
                        "source_name": "Test News",
                        "url": "https://example.com/news",
                        "published_at": "2026-08-11T10:00:00+00:00",
                        "retrieved_at": "2026-08-12T10:00:00+00:00",
                        "provider": "test-provider",
                        "symbol": "HDFCBANK",
                        "summary": "Results improved.",
                        "category": "earnings",
                    }
                ]
            },
        )

    provider = HttpNewsProvider(
        base_url="https://news.test",
        client=make_client(handler),
    )

    result = await provider.search_news(
        "HDFC Bank",
        date(2026, 8, 10),
        date(2026, 8, 11),
    )

    assert len(result) == 1
    assert result[0].title == "HDFC Bank earnings"
    assert result[0].source_name == "Test News"
    assert result[0].symbol == "HDFCBANK"
    assert result[0].summary == "Results improved."
    assert result[0].category == "earnings"


@pytest.mark.asyncio
async def test_company_news_normalizes_symbol_and_dates() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/company"
        assert request.url.params["symbol"] == "HDFCBANK"
        assert request.url.params["start_date"] == "2026-08-10"
        assert request.url.params["end_date"] == "2026-08-11"

        return httpx.Response(
            200,
            json={"articles": []},
        )

    provider = HttpNewsProvider(
        base_url="https://news.test",
        client=make_client(handler),
    )

    result = await provider.get_company_news(
        " hdfcbank ",
        date(2026, 8, 10),
        date(2026, 8, 11),
    )

    assert result == []


@pytest.mark.asyncio
async def test_empty_results_return_empty_list() -> None:
    provider = HttpNewsProvider(
        base_url="https://news.test",
        client=make_client(
            lambda request: httpx.Response(
                200,
                json={"articles": []},
            )
        ),
    )

    result = await provider.search_news("nothing")

    assert result == []


@pytest.mark.asyncio
async def test_malformed_json_raises_response_error() -> None:
    provider = HttpNewsProvider(
        base_url="https://news.test",
        client=make_client(
            lambda request: httpx.Response(
                200,
                content=b"not-json",
            )
        ),
    )

    with pytest.raises(DataProviderResponseError):
        await provider.search_news("HDFC")


@pytest.mark.asyncio
async def test_malformed_article_raises_response_error() -> None:
    provider = HttpNewsProvider(
        base_url="https://news.test",
        client=make_client(
            lambda request: httpx.Response(
                200,
                json={
                    "articles": [
                        {"summary": "Missing title and source"}
                    ]
                },
            )
        ),
    )

    with pytest.raises(DataProviderResponseError):
        await provider.search_news("HDFC")


@pytest.mark.asyncio
async def test_timeout_raises_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    provider = HttpNewsProvider(
        base_url="https://news.test",
        client=make_client(handler),
    )

    with pytest.raises(DataProviderUnavailableError):
        await provider.search_news("HDFC")
