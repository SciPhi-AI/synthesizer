"""A module for interfacing with Ollama"""
import logging

from synthesizer.interface.base import LLMInterface, LLMProviderName
from synthesizer.interface.llm_interface_manager import llm_interface
from synthesizer.llm import GenerationConfig, OllamaConfig, OllamaLLM

logger = logging.getLogger(__name__)


@llm_interface
class OllamaLLMInterface(LLMInterface):
    """A class to interface with Ollama."""

    provider_name = LLMProviderName.OLLAMA
    system_message = "You are a helpful assistant."

    def __init__(
        self,
        config: OllamaConfig,
        *args,
        **kwargs,
    ) -> None:
        self.config = config
        self._model = OllamaLLM(config)

    def get_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get a completion from the Ollama based on the provided prompt."""

        logger.debug(
            f"Getting completion from Ollama for model={generation_config.model_name}"
        )
        if "instruct" in generation_config.model_name:
            return self.model.get_instruct_completion(
                prompt, generation_config
            )
        else:
            return self._model.get_chat_completion(
                [
                    {
                        "role": "system",
                        "content": OllamaLLMInterface.system_message,
                    },
                    {"role": "user", "content": prompt},
                ],
                generation_config,
            )

    def get_chat_completion(
        self, conversation: list[dict], generation_config: GenerationConfig
    ) -> str:
        raise NotImplementedError(
            "Chat completion not yet implemented for Ollama."
        )

    @property
    def model(self) -> OllamaLLM:
        return self._model
