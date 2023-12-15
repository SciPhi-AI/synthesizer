"""A module for interfacing with local vLLM models"""
import logging
from typing import List

from synthesizer.interface.base import LLMInterface, LLMProviderName
from synthesizer.interface.llm_interface_manager import llm_interface
from synthesizer.llm import GenerationConfig, vLLM, vLLMConfig

logger = logging.getLogger(__name__)


@llm_interface
class vLLMInterface(LLMInterface):
    """A class to interface with local vLLM models."""

    provider_name = LLMProviderName.VLLM
    model_name = "mistralai/Mistral-7B-Instruct-v0.1"

    def __init__(self, config: vLLMConfig, *args, **kwargs) -> None:
        self._model = vLLM(config)

    def get_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get a completion from the local vLLM provider."""

        logger.debug(
            f"Requesting completion from local vLLM with prompt={prompt}"
        )
        return self.model.get_instruct_completion(prompt, generation_config)

    def get_batch_completion(
        self, prompts: List[str], generation_config: GenerationConfig
    ) -> List[str]:
        """Get a batch completion from the local vLLM provider."""

        logger.debug(
            f"Requesting batch completion from local vLLM with prompts={prompts}"
        )
        return self.model.get_batch_instruct_completion(
            prompts, generation_config
        )

    def get_chat_completion(
        self, conversation: List[dict], generation_config: GenerationConfig
    ) -> str:
        """Get a conversation completion from the local vLLM provider."""
        raise NotImplementedError(
            "Chat completion not yet implemented for vLLM."
        )

    @property
    def model(self) -> vLLM:
        return self._model
