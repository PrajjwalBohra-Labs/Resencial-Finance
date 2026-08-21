from __future__ import annotations

from datetime import date

from backend.app.data.providers.bonds import BondDataProvider
from backend.app.data.providers.filings import FilingsProvider
from backend.app.data.providers.macro import MacroDataProvider
from backend.app.data.providers.news import NewsProvider
from backend.app.domain.research_sources import (
    BondRecord,
    BondYieldRecord,
    FilingRecord,
    MacroObservation,
    NewsRecord,
)


class InMemoryResearchProvider(
    NewsProvider,
    FilingsProvider,
    MacroDataProvider,
    BondDataProvider,
):
    """
    Deterministic normalized provider for advanced research.

    This provider intentionally performs no network access. It gives the
    research layer a concrete provider implementation while external
    provider adapters are introduced separately.
    """

    def __init__(
        self,
        *,
        news: list[NewsRecord] | None = None,
        filings: list[FilingRecord] | None = None,
        macro: list[MacroObservation] | None = None,
        bonds: list[BondRecord] | None = None,
        bond_yields: list[BondYieldRecord] | None = None,
    ) -> None:
        self._news = list(news or [])
        self._filings = list(filings or [])
        self._macro = list(macro or [])
        self._bonds = list(bonds or [])
        self._bond_yields = list(bond_yields or [])

    @property
    def name(self) -> str:
        return "in_memory_research"

    async def search_news(
        self,
        query: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[NewsRecord]:
        normalized_query = query.strip().lower()

        return [
            record
            for record in self._news
            if (
                not normalized_query
                or normalized_query in record.title.lower()
                or normalized_query in record.summary.lower()
                or (
                    record.symbol is not None
                    and normalized_query in record.symbol.lower()
                )
            )
            and self._in_date_range(
                record.published_at.date()
                if record.published_at is not None
                else None,
                start_date,
                end_date,
            )
        ]

    async def get_company_news(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[NewsRecord]:
        normalized_symbol = symbol.strip().upper()

        return [
            record
            for record in self._news
            if record.symbol is not None
            and record.symbol.upper() == normalized_symbol
            and self._in_date_range(
                record.published_at.date()
                if record.published_at is not None
                else None,
                start_date,
                end_date,
            )
        ]

    async def search_filings(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[FilingRecord]:
        normalized_symbol = symbol.strip().upper()

        return [
            record
            for record in self._filings
            if record.symbol.upper() == normalized_symbol
            and self._in_date_range(
                record.filing_date,
                start_date,
                end_date,
            )
        ]

    async def get_latest_filing(
        self,
        symbol: str,
    ) -> FilingRecord | None:
        normalized_symbol = symbol.strip().upper()

        matches = [
            record
            for record in self._filings
            if record.symbol.upper() == normalized_symbol
        ]

        if not matches:
            return None

        return max(
            matches,
            key=lambda record: record.filing_date or date.min,
        )

    async def get_series(
        self,
        series_name: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[MacroObservation]:
        normalized_name = series_name.strip().lower()

        return [
            observation
            for observation in self._macro
            if observation.series_name.lower() == normalized_name
            and self._in_date_range(
                observation.observation_date,
                start_date,
                end_date,
            )
        ]

    async def get_latest(
        self,
        series_name: str,
    ) -> MacroObservation | None:
        normalized_name = series_name.strip().lower()

        matches = [
            observation
            for observation in self._macro
            if observation.series_name.lower() == normalized_name
        ]

        if not matches:
            return None

        return max(
            matches,
            key=lambda observation: observation.observation_date,
        )

    async def get_bond(
        self,
        identifier: str,
    ) -> BondRecord | None:
        normalized_identifier = identifier.strip().upper()

        for bond in self._bonds:
            if bond.identifier.upper() == normalized_identifier:
                return bond

        return None

    async def get_bond_yield(
        self,
        identifier: str,
    ) -> BondYieldRecord | None:
        normalized_identifier = identifier.strip().upper()

        matches = [
            record
            for record in self._bond_yields
            if record.identifier.upper() == normalized_identifier
        ]

        if not matches:
            return None

        return max(
            matches,
            key=lambda record: record.observation_date or date.min,
        )

    async def search_bonds(
        self,
        query: str,
    ) -> list[BondRecord]:
        normalized_query = query.strip().lower()

        if not normalized_query:
            return list(self._bonds)

        return [
            bond
            for bond in self._bonds
            if (
                normalized_query in bond.identifier.lower()
                or (
                    bond.issuer is not None
                    and normalized_query in bond.issuer.lower()
                )
                or (
                    bond.isin is not None
                    and normalized_query in bond.isin.lower()
                )
            )
        ]

    @staticmethod
    def _in_date_range(
        value: date | None,
        start_date: date | None,
        end_date: date | None,
    ) -> bool:
        if value is None:
            return start_date is None and end_date is None

        if start_date is not None and value < start_date:
            return False

        if end_date is not None and value > end_date:
            return False

        return True


__all__ = ["InMemoryResearchProvider"]
