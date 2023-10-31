"""A module for interfacing with local vLLM models"""
import logging
from typing import List

from sciphi.interface.base import LLMInterface, LLMProviderName
from sciphi.interface.llm_interface_manager import llm_interface
from sciphi.llm import GenerationConfig, vLLM, vLLMConfig

logger = logging.getLogger(__name__)


@llm_interface
class vLLMInterface(LLMInterface):
    """A class to interface with local vLLM models."""

    provider_name = LLMProviderName.VLLM
    model_name = "SciPhi/SciPhi-Self-RAG-Mistral-7B-32k"

    def __init__(self, config: vLLMConfig, *args, **kwargs) -> None:
        self._model = vLLM(config)

    def get_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get a completion from the local vLLM provider."""

        logger.debug(
            f"Requesting completion from local vLLM with model={self._model.config.model_name} and prompt={prompt}"
        )
        return self.model.get_instruct_completion(prompt)

    def get_batch_completion(
        self, prompts: List[str], generation_config: GenerationConfig
    ) -> List[str]:
        """Get a batch completion from the local vLLM provider."""

        logger.debug(
            f"Requesting batch completion from local vLLM with model={self._model.config.model_name} and prompts={prompts}"
        )
        return self.model.get_batch_instruct_completion(prompts)

    def get_chat_completion(
        self, conversation: List[dict], generation_config: GenerationConfig
    ) -> str:
        """Get a conversation completion from the local vLLM provider."""

        logger.debug(
            f"Requesting chat completion from local vLLM with model={self._model.config.model_name} and prompts={prompts}"
        )
        return self.model.get_instruct_completion(prompt)

    @property
    def model(self) -> vLLM:
        return self._model
