from typing import Any

import httpx

from backend.app.core.exceptions import LLMProviderError
from backend.app.domain.llm import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    LLMUsage,
)


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 120.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def provider_name(self) -> str:
        return "ollama"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [
                {
                    "role": message.role.value,
                    "content": message.content,
                }
                for message in request.messages
            ],
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
            ) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )

            response.raise_for_status()
            data = response.json()

        except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
            raise LLMProviderError(
                "Ollama could not fulfill the research request."
            ) from exc

        message = data.get("message", {})
        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise LLMProviderError(
                "Ollama returned an empty or invalid response."
            )

        prompt_tokens = int(data.get("prompt_eval_count", 0))
        completion_tokens = int(data.get("eval_count", 0))

        return LLMResponse(
            model=str(data.get("model", request.model)),
            content=content,
            provider=self.provider_name,
            usage=LLMUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
        )
