"""A module for interfacing with the Anthropic API"""
from sciphi.interface.base import LLMInterface, ProviderName
from sciphi.interface.interface_manager import llm_provider
from sciphi.llm import AnthropicConfig, AnthropicLLM, ModelName


@llm_provider
class AnthropicLLMInterface(LLMInterface):
    """A class to interface with the Anthropic API."""

    provider_name = ProviderName.ANTHROPIC
    supported_models = [
        ModelName.CLAUDE_INSTANT_1,
        ModelName.CLAUDE_2,
    ]

    def __init__(
        self,
        config: AnthropicConfig = AnthropicConfig(),
    ) -> None:
        super()
        self._model = AnthropicLLM(
            config,
        )

    def get_completion(self, prompt: str) -> str:
        """Get a completion from the remote Anthropic provider."""
        return self.model.get_instruct_completion(prompt)

    @property
    def model(self) -> AnthropicLLM:
        return self._model
