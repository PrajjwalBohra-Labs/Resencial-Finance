from abc import ABC, abstractmethod
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: MessageRole
    content: str = Field(min_length=1)


class LLMRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(min_length=1)
    messages: list[ChatMessage] = Field(min_length=1)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)


class LLMUsage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)


class LLMResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str
    content: str
    provider: str
    usage: LLMUsage = Field(default_factory=LLMUsage)


class LLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier."""
        raise NotImplementedError

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response for an LLM request."""
        raise NotImplementedError
