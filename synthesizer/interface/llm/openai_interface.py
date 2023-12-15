"""A module for interfacing with the OpenAI API"""
import logging

from synthesizer.interface.base import LLMInterface, LLMProviderName
from synthesizer.interface.llm_interface_manager import llm_interface
from synthesizer.llm import GenerationConfig, OpenAIConfig, OpenAILLM

logger = logging.getLogger(__name__)


@llm_interface
class OpenAILLMInterface(LLMInterface):
    """A class to interface with the OpenAI API."""

    provider_name = LLMProviderName.OPENAI
    system_message = "You are a helpful assistant."

    def __init__(
        self,
        config: OpenAIConfig,
        *args,
        **kwargs,
    ) -> None:
        self.config = config
        self._model = OpenAILLM(config)

    def get_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get a completion from the OpenAI API based on the provided prompt."""

        logger.debug(
            f"Getting completion from OpenAI API for model={generation_config.model_name}"
        )
        if "instruct" in generation_config.model_name:
            return self.model.get_instruct_completion(
                prompt, generation_config
            )
        else:
            return self._model.get_chat_completion(
                [
                    {
                        "role": "system",
                        "content": OpenAILLMInterface.system_message,
                    },
                    {"role": "user", "content": prompt},
                ],
                generation_config,
            )

    def get_chat_completion(
        self, conversation: list[dict], generation_config: GenerationConfig
    ) -> str:
        raise NotImplementedError(
            "Chat completion not yet implemented for OpenAI."
        )

    @property
    def model(self) -> OpenAILLM:
        return self._model
