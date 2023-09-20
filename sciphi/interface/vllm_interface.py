"""A module for interfacing with local vLLM models"""
import logging

from sciphi.interface.base import LLMInterface, ProviderName
from sciphi.interface.interface_manager import llm_provider
from sciphi.llm import vLLM, vLLMConfig

logger = logging.getLogger(__name__)


@llm_provider
class HuggingFaceLLMInterface(LLMInterface):
    """A class to interface with local vLLM models."""

    provider_name = ProviderName.VLLM

    def __init__(
        self,
        config: vLLMConfig = vLLMConfig(),
    ) -> None:
        self._model = vLLM(config)

    def get_completion(self, prompt: str) -> str:
        """Get a completion from the local vLLM provider."""

        logger.debug(
            f"Requesting completion from local vLLM with model={self._model.config.model_name} and prompt={prompt}"
        )
        return self.model.get_instruct_completion(prompt)

    @property
    def model(self) -> vLLM:
        return self._model
