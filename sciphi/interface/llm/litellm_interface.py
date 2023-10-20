"""A module for interfacing with LiteLLM"""
import logging

from sciphi.interface.base import LLMInterface, LLMProviderName, ModelName
from sciphi.interface.llm_interface_manager import llm_interface
from sciphi.llm import LiteLLM, LiteLLMConfig

logger = logging.getLogger(__name__)


@llm_interface
class LiteLLMInterface(LLMInterface):
    """A class to interface with the LiteLLM API."""

    instruct_models = [
        ModelName.GPT_3p5_TURBO_INSTRUCT,
    ]
    llm_provider_name = LLMProviderName.LITE_LLM
    supported_models = []

    system_message = "You are a helpful assistant."

    def __init__(
        self,
        config: LiteLLMConfig,
    ) -> None:
        self.config = config
        self._model = LiteLLM(config)

    def get_completion(self, prompt: str) -> str:
        """Get a completion from LiteLLM based on the provided prompt."""

        logger.debug(
            f"Getting completion from LiteLLM for model={self.config.model_name}"
        )
        if ModelName(self.config.model_name) in self.instruct_models:
            return self.model.get_instruct_completion(prompt)
        else:
            return self._model.get_chat_completion(
                [
                    {
                        "role": "system",
                        "content": LiteLLMInterface.system_message,
                    },
                    {"role": "user", "content": prompt},
                ]
            )

    @property
    def model(self) -> LiteLLM:
        return self._model
