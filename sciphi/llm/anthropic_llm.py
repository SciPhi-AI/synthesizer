"""A module for creating Anthropic models."""
from dataclasses import dataclass

from sciphi.core import ProviderName
from sciphi.llm.base import LLM, LLMConfig
from sciphi.llm.config_manager import model_config


@model_config
@dataclass
class AnthropicConfig(LLMConfig):
    """Configuration for Anthropic models."""

    # Base
    provider_name: ProviderName = ProviderName.ANTHROPIC
    model_name: str = "claude-2"
    temperature: float = 0.7
    top_p: float = 1.0

    # Anthropic Extras
    do_stream: bool = False
    max_tokens_to_sample: int = 256


class AnthropicLLM(LLM):
    """A concrete class for creating Anthropic models."""

    def __init__(
        self,
        config: AnthropicConfig,
    ) -> None:
        super().__init__(
            config,
        )
        try:
            from anthropic import Anthropic
        except:
            raise ImportError(
                "Please install the anthropic package before attempting to run with an Anthropic model. This can be accomplished via `poetry install -E anthropic_support, ...OTHER_DEPENDENCY_HERE`."
            )

        self.anthropic = Anthropic()
        if not self.anthropic.api_key:
            raise ValueError(
                "Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable."
            )

    def get_completion(self, prompt: str) -> str:
        """Get a completion from the Anthropic API based on the provided messages."""

        from anthropic import AI_PROMPT, HUMAN_PROMPT

        formatted_prompt = f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}"

        completion = self.anthropic.completions.create(
            model=self.config.model_name,
            prompt=formatted_prompt,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            max_tokens_to_sample=self.config.max_tokens_to_sample,
            stream=self.config.do_stream,
        )  # type: ignore

        return completion.completion
