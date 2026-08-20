from backend.app.domain.llm import (
    ChatMessage,
    LLMProvider,
    LLMRequest,
    MessageRole,
)
from backend.app.domain.research import ResearchAnswer, ResearchContext
from backend.app.domain.research_validation import ResearchValidationResult
from backend.app.services.research_answer_validator import (
    ResearchAnswerValidator,
)
from backend.app.services.research_correction_prompt import (
    build_correction_prompt,
)
from backend.app.services.research_prompt_builder import ResearchPromptBuilder


class ResearchEngine:
    """Turns research context into a structured research answer."""

    def __init__(
        self,
        *,
        llm_provider: LLMProvider,
        prompt_builder: ResearchPromptBuilder | None = None,
        validator: ResearchAnswerValidator | None = None,
        model: str = "llama3.2",
        temperature: float = 0.2,
    ) -> None:
        self._llm_provider = llm_provider
        self._prompt_builder = (
            prompt_builder or ResearchPromptBuilder()
        )
        self._validator = validator or ResearchAnswerValidator()
        self._model = model
        self._temperature = temperature

    def _build_request(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMRequest:
        return LLMRequest(
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

    async def research(
        self,
        context: ResearchContext,
    ) -> ResearchAnswer:
        system_prompt, user_prompt = self._prompt_builder.build(
            context
        )

        request = self._build_request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        response = await self._llm_provider.generate(request)

        validation: ResearchValidationResult = (
            self._validator.validate(
                context=context,
                answer=response.content,
            )
        )

        total_usage = response.usage

        if not validation.passed:
            correction_prompt = build_correction_prompt(
                original_prompt=user_prompt,
                validation=validation,
            )

            correction_request = self._build_request(
                system_prompt=system_prompt,
                user_prompt=correction_prompt,
            )

            corrected_response = await self._llm_provider.generate(
                correction_request
            )

            corrected_validation = self._validator.validate(
                context=context,
                answer=corrected_response.content,
            )

            response = corrected_response
            validation = corrected_validation
            total_usage = response.usage.model_copy(
                update={
                    "prompt_tokens": (
                        total_usage.prompt_tokens
                        + corrected_response.usage.prompt_tokens
                    ),
                    "completion_tokens": (
                        total_usage.completion_tokens
                        + corrected_response.usage.completion_tokens
                    ),
                    "total_tokens": (
                        total_usage.total_tokens
                        + corrected_response.usage.total_tokens
                    ),
                }
            )

        return ResearchAnswer(
            question=context.request.question,
            answer=response.content,
            model=response.model,
            provider=response.provider,
            evidence_count=len(context.evidence),
            evidence=context.evidence,
            analytical_findings=context.analytical_findings,
            usage=total_usage,
            validation=validation,
        )


