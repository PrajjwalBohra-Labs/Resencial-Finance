from backend.app.data.providers.bonds import BondDataProvider
from backend.app.domain.evidence import Evidence
from backend.app.domain.evidence_factory import (
    create_bond_evidence,
    create_bond_yield_evidence,
)
from backend.app.domain.research import ResearchRequest
from backend.app.ports.bond_evidence import BondEvidencePort


class BondEvidenceAdapter(BondEvidencePort):
    """Convert normalized bond-provider records into research evidence."""

    def __init__(self, provider: BondDataProvider) -> None:
        self._provider = provider

    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        evidence: list[Evidence] = []
        seen: set[str] = set()

        for identifier in request.symbols:
            bond = await self._provider.get_bond(identifier)
            if bond is not None and bond.identifier not in seen:
                evidence.append(create_bond_evidence(bond))
                seen.add(bond.identifier)

            yield_record = await self._provider.get_bond_yield(
                identifier
            )
            if yield_record is not None:
                evidence.append(
                    create_bond_yield_evidence(yield_record)
                )

        query = request.question.strip()
        if query:
            for bond in await self._provider.search_bonds(query):
                if bond.identifier in seen:
                    continue

                evidence.append(create_bond_evidence(bond))
                seen.add(bond.identifier)

                yield_record = await self._provider.get_bond_yield(
                    bond.identifier
                )
                if yield_record is not None:
                    evidence.append(
                        create_bond_yield_evidence(yield_record)
                    )

        return evidence
