"""A module for interfacing with the Anthropic API"""
from sciphi.interface.base import LLMInterface, LLMProviderName
from sciphi.interface.llm_interface_manager import llm_interface
from sciphi.llm import (
    AnthropicConfig,
    AnthropicLLM,
    GenerationConfig,
    ModelName,
)


@llm_interface
class AnthropicLLMInterface(LLMInterface):
    """A class to interface with the Anthropic API."""

    provider_name = LLMProviderName.ANTHROPIC
    supported_models = [
        ModelName.CLAUDE_INSTANT_1,
        ModelName.CLAUDE_2,
    ]

    def __init__(
        self,
        config: AnthropicConfig,
        *args,
        **kwargs,
    ) -> None:
        super()
        self._model = AnthropicLLM(
            config,
        )

    def get_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get a completion from the remote Anthropic provider."""
        return self.model.get_instruct_completion(prompt, generation_config)

    def get_chat_completion(
        self, conversation: list[dict], generation_config: GenerationConfig
    ) -> str:
        """Get a chat completion from the remote Anthropic provider."""
        raise NotImplementedError(
            "Chat completion not yet implemented for Anthropic."
        )

    @property
    def model(self) -> AnthropicLLM:
        return self._model
