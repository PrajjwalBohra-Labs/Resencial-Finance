from abc import abstractmethod

from backend.app.data.providers.base import DataProvider
from backend.app.domain.research_sources import BondRecord, BondYieldRecord


class BondDataProvider(DataProvider):
    """Interface for bond and fixed-income data providers."""

    @abstractmethod
    async def get_bond(
        self,
        identifier: str,
    ) -> BondRecord | None:
        """Return normalized bond information."""
        raise NotImplementedError

    @abstractmethod
    async def get_bond_yield(
        self,
        identifier: str,
    ) -> BondYieldRecord | None:
        """Return current or latest available bond-yield information."""
        raise NotImplementedError

    @abstractmethod
    async def search_bonds(
        self,
        query: str,
    ) -> list[BondRecord]:
        """Search available fixed-income instruments."""
        raise NotImplementedError
