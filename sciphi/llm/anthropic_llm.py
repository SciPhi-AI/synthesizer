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
            from anthropic import AI_PROMPT, HUMAN_PROMPT, Anthropic
        except ImportError:
            raise ImportError(
                "Please install the anthropic package before attempting to run with an Anthropic model. This can be accomplished via `poetry install -E anthropic_support, ...OTHER_DEPENDENCIES_HERE`."
            )

        self.raw_prompt = HUMAN_PROMPT + " {instruction} " + AI_PROMPT
        self.anthropic = Anthropic()

        if not self.anthropic.api_key:
            raise ValueError(
                "Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable."
            )

        # set the config here, again, for typing purposes
        if not isinstance(self.config, AnthropicConfig):
            raise ValueError(
                "The provided config must be an instance of AnthropicConfig."
            )
        self.config: AnthropicConfig = config

    def get_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Get a chat completion from the remote Anthropic API."""
        raise NotImplementedError(
            "Chat completion is not yet supported for Anthropic."
        )

    def get_instruct_completion(self, instruction: str) -> str:
        """Get an instruction completion from the remote Anthropic API."""

        formatted_prompt = self.raw_prompt.format(instruction=instruction)
        # TODO - Why does anthropic completion endpoint create a type error?
        completion = self.anthropic.completions.create(
            model=self.config.model_name,
            prompt=formatted_prompt,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            max_tokens_to_sample=self.config.max_tokens_to_sample,
            stream=self.config.do_stream,
        )  # type: ignore
        return completion.completion
