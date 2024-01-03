"""A module for interfacing with the SciPhi API"""
import logging

from synthesizer.interface.base import LLMInterface, LLMProviderName
from synthesizer.interface.llm_interface_manager import llm_interface
from synthesizer.llm import GenerationConfig, SciPhiConfig, SciPhiLLM

logger = logging.getLogger(__name__)


@llm_interface
class SciPhiLLMInterface(LLMInterface):
    """A class to interface with the SciPhi API."""

    provider_name = LLMProviderName.SCIPHI

    def __init__(
        self,
        config: SciPhiConfig,
        *args,
        **kwargs,
    ) -> None:
        self.config = config
        self._model = SciPhiLLM(config)

    def get_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get a completion from the SciPhi API based on the provided prompt."""

        logger.debug(
            f"Getting completion from SciPhi API for model={generation_config.model_name}"
        )
        return self.model.get_instruct_completion(prompt, generation_config)

    def get_chat_completion(
        self, conversation: list[dict], generation_config: GenerationConfig
    ) -> str:
        raise NotImplementedError(
            "Chat completion not yet implemented for SciPhi."
        )

    @property
    def model(self) -> SciPhiLLM:
        return self._model
