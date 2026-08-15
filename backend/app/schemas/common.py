from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Source(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: str
    url: str | None = None
    provider: str | None = None


class DataFreshness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observed_at: datetime | None = None
    retrieved_at: datetime | None = None
    status: str
