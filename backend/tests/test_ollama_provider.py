import httpx
import pytest

from backend.app.domain.llm import (
    ChatMessage,
    LLMRequest,
    MessageRole,
)
from backend.app.llm.ollama import OllamaProvider


@pytest.mark.asyncio
async def test_ollama_provider_name() -> None:
    provider = OllamaProvider()

    assert provider.provider_name == "ollama"


@pytest.mark.asyncio
async def test_ollama_provider_generates_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    async def fake_post(
        self: httpx.AsyncClient,
        url: str,
        **kwargs: object,
    ) -> httpx.Response:
        captured["url"] = url
        captured["json"] = kwargs["json"]

        return httpx.Response(
            status_code=200,
            json={
                "model": "test-model",
                "message": {
                    "role": "assistant",
                    "content": "This is a research response.",
                },
            },
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    provider = OllamaProvider(
        base_url="http://127.0.0.1:11434",
    )

    request = LLMRequest(
        model="test-model",
        messages=[
            ChatMessage(
                role=MessageRole.SYSTEM,
                content="You are a financial research assistant.",
            ),
            ChatMessage(
                role=MessageRole.USER,
                content="Research HDFC Bank.",
            ),
        ],
    )

    result = await provider.generate(request)

    assert result.provider == "ollama"
    assert result.model == "test-model"
    assert result.content == "This is a research response."

    assert captured["url"] == (
        "http://127.0.0.1:11434/api/chat"
    )

    payload = captured["json"]

    assert isinstance(payload, dict)
    assert payload["model"] == "test-model"
    assert payload["stream"] is False
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"


@pytest.mark.asyncio
async def test_ollama_provider_rejects_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_post(
        self: httpx.AsyncClient,
        url: str,
        **kwargs: object,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "model": "test-model",
                "message": {
                    "role": "assistant",
                    "content": "",
                },
            },
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    provider = OllamaProvider()

    request = LLMRequest(
        model="test-model",
        messages=[
            ChatMessage(
                role=MessageRole.USER,
                content="Research HDFC Bank.",
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match="empty or invalid response",
    ):
        await provider.generate(request)
