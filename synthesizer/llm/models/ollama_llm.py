"""A module for creating Ollama model abstractions."""
import os
from dataclasses import dataclass

from litellm import completion

from synthesizer.core import LLMProviderName
from synthesizer.llm.base import LLM, GenerationConfig, LLMConfig
from synthesizer.llm.config_manager import model_config


@model_config
@dataclass
class OllamaConfig(LLMConfig):
    """Configuration for Ollama models."""

    # Base
    provider_name: LLMProviderName = LLMProviderName.OLLAMA
    api_base: str = "http://localhost:11434"


class OllamaLLM(LLM):
    """A concrete class for creating Ollama models."""

    def __init__(
        self,
        config: OllamaConfig,
        *args,
        **kwargs,
    ) -> None:
        super().__init__()
        self.config: OllamaConfig = config

        # set the config here, again, for typing purposes
        if not isinstance(self.config, OllamaConfig):
            raise ValueError(
                "The provided config must be an instance of OllamaConfig."
            )

    def get_chat_completion(
        self,
        messages: list[dict[str, str]],
        generation_config: GenerationConfig,
    ) -> str:
        """Get a chat completion from Ollama based on the provided prompt."""

        # Create the chat completion
        response = completion(
            model="ollama/mistral",
            messages=messages,
            api_base=self.config.api_base,
            stream=generation_config.do_stream,
        )

        return response.choices[0].message["content"]

    def get_instruct_completion(
        self,
        messages: list[dict[str, str]],
        generation_config: GenerationConfig,
    ) -> str:
        """Get an instruction completion from Ollama."""
        raise NotImplementedError(
            "Instruction completion is not yet supported for Ollama."
        )
