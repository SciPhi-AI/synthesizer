"""A module for providing zero-shot completions from the OpenAI API."""
import logging

from sci_phi.interface.base import LLMInterface, ProviderName
from sci_phi.interface.interface_manager import llm_provider

from sci_phi.llm import HuggingFaceConfig, HuggingFaceLLM, ModelName

logger = logging.getLogger(__name__)


@llm_provider
class HuggingFaceLLMInterface(LLMInterface):
    """A class to provide zero-shot completions from local HuggingFacemodels."""

    provider_name = ProviderName.HUGGING_FACE

    def __init__(
        self,
        config: HuggingFaceConfig = HuggingFaceConfig(),
    ) -> None:
        self._model = HuggingFaceLLM(config)

    def get_completion(self, prompt: str) -> str:
        """Get a completion from the Local HuggingFace API based on the provided prompt."""
        logger.info(
            f"Getting completion from Local HuggingFace API for model={self._model.config.model_name}"
        )
        return self.model.get_completion(prompt)

    @property
    def model(self) -> HuggingFaceLLM:
        return self._model
