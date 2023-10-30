"""A module for interfacing with local HuggingFace models"""
import logging

from sciphi.interface.base import LLMInterface, LLMProviderName
from sciphi.interface.llm_interface_manager import llm_interface
from sciphi.llm import GenerationConfig, HuggingFaceConfig, HuggingFaceLLM

logger = logging.getLogger(__name__)


@llm_interface
class HuggingFaceLLMInterface(LLMInterface):
    """A class to interface with local HuggingFace models."""

    provider_name = LLMProviderName.HUGGING_FACE

    def __init__(self, config: HuggingFaceConfig, *args, **kwargs) -> None:
        self._model = HuggingFaceLLM(config)

    def get_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get a completion from the local HuggingFace provider."""

        logger.debug(
            f"Requesting completion from local HuggingFace with model={self._model.config.model_name} and prompt={prompt}"
        )
        return self.model.get_instruct_completion(prompt, generation_config)

    def get_chat_completion(
        self, conversation: list[dict], generation_config: GenerationConfig
    ) -> str:
        """Get a chat completion from the local HuggingFace provider."""
        raise NotImplementedError(
            "Chat completion not yet implemented for HuggingFace."
        )

    def get_chat_completion(
        self, conversation: list[dict], generation_config: GenerationConfig
    ) -> str:
        """Get a chat completion from the local HuggingFace provider."""
        raise NotImplementedError(
            "Chat completion not yet implemented for HuggingFace."
        )

    @property
    def model(self) -> HuggingFaceLLM:
        return self._model
