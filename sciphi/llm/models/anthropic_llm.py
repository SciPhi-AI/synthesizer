"""A module for creating Anthropic models."""
from dataclasses import dataclass

from sciphi.core import LLMProviderName
from sciphi.llm.base import LLM, LLMConfig, GenerationConfig
from sciphi.llm.config_manager import model_config


@model_config
@dataclass
class AnthropicConfig(LLMConfig):
    """Configuration for Anthropic models."""

    # Base
    provider_name: LLMProviderName = LLMProviderName.ANTHROPIC
    model_name: str = "claude-2"

    # Anthropic Extras
    do_stream: bool = False
    max_tokens_to_sample: int = 256


class AnthropicLLM(LLM):
    """A concrete class for creating Anthropic models."""

    def __init__(
        self,
        config: AnthropicConfig,
    ) -> None:
        super().__init__()
        try:
            from anthropic import AI_PROMPT, HUMAN_PROMPT, Anthropic
        except ImportError:
            raise ImportError(
                "Please install the anthropic package before attempting to run with an Anthropic model. This can be accomplished via `poetry install -E anthropic_support, ...OTHER_DEPENDENCIES_HERE`."
            )

        self.raw_prompt = HUMAN_PROMPT + " {instruction} " + AI_PROMPT
        self.anthropic = Anthropic()
        self.config: AnthropicConfig = config

        if not self.anthropic.api_key:
            raise ValueError(
                "Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable."
            )

        # set the config here, again, for typing purposes
        if not isinstance(self.config, AnthropicConfig):
            raise ValueError(
                "The provided config must be an instance of AnthropicConfig."
            )

    def get_chat_completion(
        self,
        messages: list[dict[str, str]],
        generation_config: GenerationConfig,
    ) -> str:
        """Get a chat completion from the remote Anthropic API."""
        raise NotImplementedError(
            "Chat completion is not yet supported for Anthropic."
        )

    def get_instruct_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get an instruction completion from the remote Anthropic API."""

        formatted_prompt = self.raw_prompt.format(instruction=prompt)
        # TODO - Why does anthropic completion endpoint create a type error?
        completion = self.anthropic.completions.create(
            model=generation_config.model_name,
            prompt=formatted_prompt,
            temperature=generation_config.temperature,
            top_p=generation_config.top_p,
            max_tokens_to_sample=generation_config.max_tokens_to_sample,
            stream=generation_config.do_stream,
        )  # type: ignore
        return completion.completion
