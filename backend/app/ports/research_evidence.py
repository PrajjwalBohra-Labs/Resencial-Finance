from abc import ABC, abstractmethod

from backend.app.domain.evidence import Evidence
from backend.app.domain.research import ResearchRequest


class NewsEvidencePort(ABC):
    @abstractmethod
    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        raise NotImplementedError


class FilingEvidencePort(ABC):
    @abstractmethod
    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        raise NotImplementedError


class MacroEvidencePort(ABC):
    @abstractmethod
    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        raise NotImplementedError


class BondEvidencePort(ABC):
    @abstractmethod
    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        raise NotImplementedError


__all__ = [
    "BondEvidencePort",
    "FilingEvidencePort",
    "MacroEvidencePort",
    "NewsEvidencePort",
]
