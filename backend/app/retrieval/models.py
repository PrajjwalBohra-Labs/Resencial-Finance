from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain.evidence import EvidenceType


class RetrievalQuery(BaseModel):
    """Structured research retrieval request."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)

    symbols: list[str] = Field(default_factory=list)
    exchange: str | None = None

    evidence_types: list[EvidenceType] = Field(default_factory=list)

    start_date: date | None = None
    end_date: date | None = None

    limit: int = Field(default=10, ge=1, le=100)

    def normalized_symbols(self) -> set[str]:
        return {
            symbol.strip().upper()
            for symbol in self.symbols
            if symbol.strip()
        }

    def normalized_exchange(self) -> str | None:
        if self.exchange is None:
            return None

        value = self.exchange.strip().upper()
        return value or None


class EvidenceChunk(BaseModel):
    """Retrievable evidence with immutable source metadata."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    text: str

    symbol: str | None = None
    exchange: str | None = None
    evidence_type: EvidenceType

    observation_date: date | None = None
    published_at: datetime | None = None
    retrieved_at: datetime

    source: str
    provider: str | None = None

    lexical_score: float = 0.0
    metadata_score: float = 0.0
    temporal_score: float = 0.0
    total_score: float = 0.0


class RetrievalResult(BaseModel):
    """Ranked evidence returned to the research pipeline."""

    model_config = ConfigDict(extra="forbid")

    query: RetrievalQuery
    chunks: list[EvidenceChunk] = Field(default_factory=list)

    @property
    def evidence_count(self) -> int:
        return len(self.chunks)
