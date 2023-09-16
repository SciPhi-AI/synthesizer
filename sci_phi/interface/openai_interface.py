"""A module for providing zero-shot completions from the OpenAI API."""
import logging

from sci_phi.interface.base import (
    LLMInterface,
    ModelName,
    ProviderName,
)
from sci_phi.interface.interface_manager import llm_provider

from sci_phi.llm import OpenAIConfig, OpenAILLM

logger = logging.getLogger(__name__)


@llm_provider
class OpenAILLMInterface(LLMInterface):
    """A class to provide zero-shot completions from the OpenAI API."""

    provider_name = ProviderName.OPENAI
    supported_models = [
        ModelName.GPT_3p5_TURBO_0301,
        ModelName.GPT_3p5_TURBO_0613,
        ModelName.GPT_3p5_TURBO,
        ModelName.GPT_4_0314,
        ModelName.GPT_4_0613,
        ModelName.GPT_4,
    ]

    def __init__(
        self,
        config: OpenAIConfig,
    ) -> None:
        self.config = config
        self._model = OpenAILLM(config)

    def get_completion(self, prompt: str) -> str:
        """Get a completion from the OpenAI API based on the provided prompt."""
        logger.info(
            f"Getting completion from OpenAI API for model={self.config.model_name}"
        )
        return self._model.get_completion(
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )

    @property
    def model(self) -> OpenAILLM:
        return self._model
