from abc import abstractmethod

from backend.app.data.providers.base import DataProvider


class BondDataProvider(DataProvider):
    """Interface for bond and fixed-income data providers."""

    @abstractmethod
    async def get_bond(
        self,
        identifier: str,
    ) -> dict[str, object] | None:
        """Return normalized bond information."""
        raise NotImplementedError

    @abstractmethod
    async def get_bond_yield(
        self,
        identifier: str,
    ) -> dict[str, object] | None:
        """Return current or latest available bond-yield information."""
        raise NotImplementedError

    @abstractmethod
    async def search_bonds(
        self,
        query: str,
    ) -> list[dict[str, object]]:
        """Search available fixed-income instruments."""
        raise NotImplementedError
