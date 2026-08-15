from abc import abstractmethod
from datetime import date

from backend.app.data.providers.base import DataProvider


class NewsProvider(DataProvider):
    """Interface for financial-news providers."""

    @abstractmethod
    async def search_news(
        self,
        query: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, object]]:
        """Search relevant financial news."""
        raise NotImplementedError

    @abstractmethod
    async def get_company_news(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, object]]:
        """Return news related to a company."""
        raise NotImplementedError
