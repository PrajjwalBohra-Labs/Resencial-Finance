from datetime import date, datetime, timezone
from typing import Any

import httpx

from backend.app.core.exceptions import (
    DataProviderResponseError,
    DataProviderRetryableError,
    DataProviderUnavailableError,
)
from backend.app.core.provider_execution import run_provider_call
from backend.app.core.config import get_settings
from backend.app.data.providers.news import NewsProvider
from backend.app.domain.research_sources import NewsRecord


class HttpNewsProvider(NewsProvider):
    """HTTP-backed financial-news provider with normalized NewsRecord output."""

    @property
    def name(self) -> str:
        return "http_news"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        settings = get_settings()

        self._base_url = (
            base_url or settings.news_api_base_url
        ).rstrip("/")
        self._api_key = (
            api_key if api_key is not None else settings.news_api_key
        )
        self._client = client
        self._owns_client = client is None

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}

        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        return headers

    @staticmethod
    def _parse_date(value: Any) -> datetime | None:
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )
            except ValueError:
                return None

        return None

    @classmethod
    def _normalize_record(
        cls,
        item: Any,
    ) -> NewsRecord:
        if not isinstance(item, dict):
            raise DataProviderResponseError(
                "News provider returned an invalid article record."
            )

        title = item.get("title")
        source_name = item.get("source_name") or item.get("source")
        retrieved_at = cls._parse_date(item.get("retrieved_at"))
        published_at = cls._parse_date(item.get("published_at"))

        if not title or not source_name:
            raise DataProviderResponseError(
                "News provider returned an article missing required metadata."
            )

        if retrieved_at is None:
            retrieved_at = datetime.now(timezone.utc)

        content = (
            item.get("summary")
            or item.get("content")
            or ""
        )

        return NewsRecord(
            title=str(title),
            source_name=str(source_name),
            url=item.get("url"),
            published_at=published_at,
            retrieved_at=retrieved_at,
            provider=str(item.get("provider") or "http_news"),
            symbol=item.get("symbol"),
            summary=str(content),
            category=item.get("category"),
        )

    async def _request(
        self,
        *,
        path: str,
        params: dict[str, Any],
    ) -> list[NewsRecord]:
        async def fetch() -> list[NewsRecord]:
            client = self._client
            owns_client = False

            if client is None:
                settings = get_settings()
                client = httpx.AsyncClient(
                    timeout=settings.provider_timeout_seconds
                )
                owns_client = True

            try:
                response = await client.get(
                    f"{self._base_url}/{path.lstrip('/')}",
                    params=params,
                    headers=self._headers(),
                )

                if response.status_code >= 500:
                    raise DataProviderRetryableError(
                        "News provider returned a transient server error."
                    )

                if response.status_code >= 400:
                    raise DataProviderUnavailableError(
                        "News provider request was rejected."
                    )

                try:
                    payload = response.json()
                except ValueError as exc:
                    raise DataProviderResponseError(
                        "News provider returned invalid JSON."
                    ) from exc

                if isinstance(payload, dict):
                    items = payload.get("articles", payload.get("results"))

                    if items is None:
                        raise DataProviderResponseError(
                            "News provider response has no article collection."
                        )
                elif isinstance(payload, list):
                    items = payload
                else:
                    raise DataProviderResponseError(
                        "News provider returned an invalid response shape."
                    )

                if not isinstance(items, list):
                    raise DataProviderResponseError(
                        "News provider article collection is invalid."
                    )

                return [
                    self._normalize_record(item)
                    for item in items
                ]

            except (
                DataProviderRetryableError,
                DataProviderUnavailableError,
                DataProviderResponseError,
            ):
                raise
            except httpx.TimeoutException as exc:
                raise DataProviderUnavailableError(
                    "News provider request timed out."
                ) from exc
            except httpx.RequestError as exc:
                raise DataProviderUnavailableError(
                    "News provider request could not be completed."
                ) from exc
            finally:
                if owns_client:
                    await client.aclose()

        return await run_provider_call(
            fetch,
            operation_name=f"{self.name}.{path}",
        )

    async def search_news(
        self,
        query: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[NewsRecord]:
        params: dict[str, Any] = {"query": query}

        if start_date is not None:
            params["start_date"] = start_date.isoformat()

        if end_date is not None:
            params["end_date"] = end_date.isoformat()

        return await self._request(
            path="search",
            params=params,
        )

    async def get_company_news(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[NewsRecord]:
        params: dict[str, Any] = {
            "symbol": symbol.strip().upper(),
        }

        if start_date is not None:
            params["start_date"] = start_date.isoformat()

        if end_date is not None:
            params["end_date"] = end_date.isoformat()

        return await self._request(
            path="company",
            params=params,
        )
