"""A module for providing zero-shot completions from the Anthropic API."""
from sciphi.interface.base import LLMInterface, ProviderName
from sciphi.interface.interface_manager import llm_provider
from sciphi.llm import AnthropicConfig, AnthropicLLM, ModelName


@llm_provider
class AnthropicLLMInterface(LLMInterface):
    """A concrete class to provide zero-shot completions from the Anthropic API."""

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
        """Get a completion from the Anthropic provider based on the provided prompt."""
        return self.model.get_completion(prompt)

    @property
    def model(self) -> AnthropicLLM:
        return self._model
