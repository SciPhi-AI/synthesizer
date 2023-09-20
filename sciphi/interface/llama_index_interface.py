"""A module for interfacing with the LlamaIndex API"""
import logging

from sciphi.interface.base import LLMInterface, ProviderName
from sciphi.interface.interface_manager import llm_provider
from sciphi.llm import LLamaIndexConfig, LlamaIndexLLM

logger = logging.getLogger(__name__)


@llm_provider
class LlamaIndexInterface(LLMInterface):
    """A class to interface with the LlamaIndex API."""

    provider_name = ProviderName.LLAMA_INDEX

    def __init__(
        self,
        config: LLamaIndexConfig,
    ) -> None:
        super().__init__(config)
        if not isinstance(config, LLamaIndexConfig):
            raise ValueError(
                f"Expected an LLamaIndexConfig, but received a {type(config)}"
            )
        self.config: LLamaIndexConfig = config
        self._model: LlamaIndexLLM = LlamaIndexLLM(config)

    def get_completion(self, prompt: str) -> str:
        """Get a completion from the LlamaIndex API based on the provided prompt."""

        logger.debug(
            f"Getting completion from LlamaIndex API for model={self.config.model_name}, data_dir={self.config.llama_data_dir}, out_store_name={self.config.llama_out_store}, chunk_size={self.config.llama_chunk_size}, top_k_similarity={self.config.llama_top_k_similarity}, and prompt={prompt}"
        )
        return self.model.get_instruct_completion(prompt)

    @property
    def model(self) -> LlamaIndexLLM:
        return self._model
