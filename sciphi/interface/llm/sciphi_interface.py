"""A module for interfacing with local vLLM models"""
import logging
from typing import List

from sciphi.interface.base import LLMInterface, LLMProviderName
from sciphi.interface.llm_interface_manager import llm_interface
from sciphi.llm import SciPhiConfig, SciPhiLLM

logger = logging.getLogger(__name__)


@llm_interface
class SciPhiInterface(LLMInterface):
    """A class to interface with local vLLM models."""

    llm_provider_name = LLMProviderName.SCIPHI

    def __init__(
        self,
        config: SciPhiConfig = SciPhiConfig(),
    ) -> None:
        self._model = SciPhiLLM(config)

    def get_completion(self, prompt: str) -> str:
        """Get a completion from the local vLLM provider."""

        logger.debug(
            f"Requesting completion from local vLLM with model={self._model.config.model_name} and prompt={prompt}"
        )
        return self.model.get_instruct_completion(prompt)

    def get_batch_completion(self, prompts: List[str]) -> List[str]:
        """Get a completion from the local vLLM provider."""

        logger.debug(
            f"Requesting completion from local vLLM with model={self._model.config.model_name} and prompts={prompts}"
        )
        return self.model.get_batch_instruct_completion(prompts)

    @property
    def model(self) -> SciPhiLLM:
        return self._model
