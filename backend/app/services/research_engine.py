from backend.app.domain.llm import (
    ChatMessage,
    LLMProvider,
    LLMRequest,
    MessageRole,
)
from backend.app.domain.research import ResearchAnswer, ResearchContext
from backend.app.services.research_prompt_builder import ResearchPromptBuilder


class ResearchEngine:
    """Turns research context into a structured research answer."""

    def __init__(
        self,
        *,
        llm_provider: LLMProvider,
        prompt_builder: ResearchPromptBuilder | None = None,
        model: str = "llama3.2",
        temperature: float = 0.2,
    ) -> None:
        self._llm_provider = llm_provider
        self._prompt_builder = (
            prompt_builder or ResearchPromptBuilder()
        )
        self._model = model
        self._temperature = temperature

    async def research(
        self,
        context: ResearchContext,
    ) -> ResearchAnswer:
        system_prompt, user_prompt = self._prompt_builder.build(
            context
        )

        request = LLMRequest(
            model=self._model,
            temperature=self._temperature,
            messages=[
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=system_prompt,
                ),
                ChatMessage(
                    role=MessageRole.USER,
                    content=user_prompt,
                ),
            ],
        )

        response = await self._llm_provider.generate(request)

        return ResearchAnswer(
            question=context.request.question,
            answer=response.content,
            model=response.model,
            provider=response.provider,
            evidence_count=len(context.evidence),
        )
