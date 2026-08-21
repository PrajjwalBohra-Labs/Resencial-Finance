from abc import abstractmethod
from datetime import date

from backend.app.data.providers.base import DataProvider
from backend.app.domain.research_sources import NewsRecord


class NewsProvider(DataProvider):
    """Interface for financial-news providers."""

    @abstractmethod
    async def search_news(
        self,
        query: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[NewsRecord]:
        """Search relevant financial news."""
        raise NotImplementedError

    @abstractmethod
    async def get_company_news(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[NewsRecord]:
        """Return news related to a company."""
        raise NotImplementedError
