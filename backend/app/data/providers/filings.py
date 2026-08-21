from abc import abstractmethod
from datetime import date

from backend.app.data.providers.base import DataProvider
from backend.app.domain.research_sources import FilingRecord


class FilingsProvider(DataProvider):
    """Interface for company and regulatory filings."""

    @abstractmethod
    async def search_filings(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[FilingRecord]:
        """Search filings for a company or issuer."""
        raise NotImplementedError

    @abstractmethod
    async def get_latest_filing(
        self,
        symbol: str,
    ) -> FilingRecord | None:
        """Return the latest relevant filing."""
        raise NotImplementedError
