from datetime import date, datetime, timezone

import pytest

from backend.app.data.evidence.bond_evidence_adapter import (
    BondEvidenceAdapter,
)
from backend.app.domain.research import ResearchRequest
from backend.app.domain.research_sources import BondRecord, BondYieldRecord


class FakeBondProvider:
    name = "fake-bonds"

    def __init__(self) -> None:
        self.bonds = [
            BondRecord(
                title="Government of India 7.18% 2033",
                source_name="fake-bond-source",
                url="https://example.test/bond/2033",
                published_at=datetime(
                    2026,
                    8,
                    11,
                    tzinfo=timezone.utc,
                ),
                retrieved_at=datetime.now(timezone.utc),
                provider=self.name,
                identifier="GOI2033",
                issuer="Government of India",
                isin="IN0020260011",
                coupon_rate=7.18,
                maturity_date=date(2033, 8, 11),
                credit_rating="SOV",
            )
        ]

        self.yields = [
            BondYieldRecord(
                identifier="GOI2033",
                yield_value=6.95,
                yield_unit="%",
                observation_date=date(2026, 8, 11),
                source_name="fake-bond-source",
                url="https://example.test/yield/2033",
                retrieved_at=datetime.now(timezone.utc),
                provider=self.name,
            )
        ]

        self.calls: list[tuple[str, str]] = []

    async def get_bond(
        self,
        identifier: str,
    ) -> BondRecord | None:
        self.calls.append(("get_bond", identifier))

        normalized = identifier.strip().upper()

        for bond in self.bonds:
            if bond.identifier.upper() == normalized:
                return bond

        return None

    async def get_bond_yield(
        self,
        identifier: str,
    ) -> BondYieldRecord | None:
        self.calls.append(("get_bond_yield", identifier))

        normalized = identifier.strip().upper()

        for record in self.yields:
            if record.identifier.upper() == normalized:
                return record

        return None

    async def search_bonds(
        self,
        query: str,
    ) -> list[BondRecord]:
        self.calls.append(("search_bonds", query))

        normalized = query.strip().lower()

        if not normalized:
            return list(self.bonds)

        return [
            bond
            for bond in self.bonds
            if (
                normalized in bond.identifier.lower()
                or (
                    bond.issuer is not None
                    and normalized in bond.issuer.lower()
                )
            )
        ]


@pytest.mark.asyncio
async def test_bond_adapter_collects_explicit_bond_and_yield() -> None:
    provider = FakeBondProvider()
    adapter = BondEvidenceAdapter(provider)

    request = ResearchRequest(
        question="Analyse the bond.",
        symbols=["GOI2033"],
    )

    evidence = await adapter.collect(request)

    assert len(evidence) == 2

    assert evidence[0].evidence_type.value == "regulatory"
    assert evidence[0].title == "Government of India 7.18% 2033"
    assert "Identifier: GOI2033" in evidence[0].content
    assert "Issuer: Government of India" in evidence[0].content
    assert "ISIN: IN0020260011" in evidence[0].content
    assert "Coupon rate: 7.18%" in evidence[0].content

    assert evidence[1].evidence_type.value == "macro"
    assert evidence[1].title == "GOI2033 bond yield"
    assert "Yield: 6.95%" in evidence[1].content
    assert "Observation date: 2026-08-11" in evidence[1].content


@pytest.mark.asyncio
async def test_bond_adapter_searches_using_research_question() -> None:
    provider = FakeBondProvider()
    adapter = BondEvidenceAdapter(provider)

    request = ResearchRequest(
        question="Government of India",
    )

    evidence = await adapter.collect(request)

    assert len(evidence) == 2

    assert ("search_bonds", "Government of India") in provider.calls
    assert ("get_bond_yield", "GOI2033") in provider.calls


@pytest.mark.asyncio
async def test_bond_adapter_does_not_duplicate_search_result() -> None:
    provider = FakeBondProvider()
    adapter = BondEvidenceAdapter(provider)

    request = ResearchRequest(
        question="Government of India",
        symbols=["GOI2033"],
    )

    evidence = await adapter.collect(request)

    assert len(evidence) == 2

    bond_evidence = [
        item
        for item in evidence
        if item.title == "Government of India 7.18% 2033"
    ]

    yield_evidence = [
        item
        for item in evidence
        if item.title == "GOI2033 bond yield"
    ]

    assert len(bond_evidence) == 1
    assert len(yield_evidence) == 1


@pytest.mark.asyncio
async def test_bond_adapter_handles_no_matches() -> None:
    provider = FakeBondProvider()
    adapter = BondEvidenceAdapter(provider)

    request = ResearchRequest(
        question="Corporate bond that does not exist",
        symbols=["UNKNOWN"],
    )

    evidence = await adapter.collect(request)

    assert evidence == []
    assert ("get_bond", "UNKNOWN") in provider.calls
    assert ("get_bond_yield", "UNKNOWN") in provider.calls
    assert (
        "search_bonds",
        "Corporate bond that does not exist",
    ) in provider.calls
