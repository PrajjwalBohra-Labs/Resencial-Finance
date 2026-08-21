from abc import ABC, abstractmethod

from backend.app.domain.evidence import Evidence
from backend.app.domain.research import ResearchRequest


class FilingEvidencePort(ABC):
    @abstractmethod
    async def collect(
        self,
        request: ResearchRequest,
    ) -> list[Evidence]:
        raise NotImplementedError
