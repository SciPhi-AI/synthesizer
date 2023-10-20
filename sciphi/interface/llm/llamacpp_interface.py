"""A module for interfacing with local vLLM models"""
import logging
from typing import List

from sciphi.interface.base import LLMInterface, LLMProviderName
from sciphi.interface.llm_interface_manager import llm_interface
from sciphi.llm import LlamaCPP, LLamaCPPConfig

logger = logging.getLogger(__name__)


@llm_interface
class LlamaCPPInterface(LLMInterface):
    """A class to interface with local LlamaCPP models."""

    llm_provider_name = LLMProviderName.LLAMACPP

    def __init__(
        self,
        config: LLamaCPPConfig = LLamaCPPConfig(),
    ) -> None:
        self._model = LlamaCPP(config)

    def get_completion(self, prompt: str) -> str:
        """Get a completion from the local LlamaCPP provider."""

        logger.debug(
            f"Requesting completion from local LlamaCPP with model={self._model.config.model_name} and prompt={prompt}"
        )
        return self.model.get_instruct_completion(prompt)

    def get_batch_completion(self, prompts: List[str]) -> List[str]:
        """Get a completion from the local LlamaCPP provider."""

        logger.debug(
            f"Requesting completion from local LlamaCPP with model={self._model.config.model_name} and prompts={prompts}"
        )
        return self.model.get_batch_instruct_completion(prompts)

    @property
    def model(self) -> LlamaCPP:
        return self._model
