"""A module for creating OpenAI models."""

from dataclasses import dataclass
from typing import Optional

import openai

from sci_phi.llm.base import (
    LLM,
    LLMConfig,
)
from sci_phi.core import ProviderName
from sci_phi.llm.config_manager import model_config


@model_config
@dataclass
class OpenAIConfig(LLMConfig):
    """Configuration for OpenAI models."""

    # Base
    provider_name: ProviderName = ProviderName.OPENAI
    model_name: str = "gpt-3.5-turbo"
    version: str = "0.1.0"
    temperature: float = 0.7
    top_p: float = 1.0

    # OpenAI Extras
    do_stream: bool = False
    max_tokens_to_sample: int = 256
    functions: Optional[list[dict]] = None


class OpenAILLM(LLM):
    """A concrete class for creating OpenAI models."""

    def __init__(
        self,
        config: OpenAIConfig,
    ) -> None:
        super().__init__(config)
        if not openai.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )

    def get_completion(self, messages: list[dict]) -> str:
        """Get a completion from the OpenAI API based on the provided messages."""
        # Create a dictionary with the default arguments
        args = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_tokens": self.config.max_tokens_to_sample,
            "stream": self.config.do_stream,
        }

        # Conditionally add the 'functions' argument if it's not None
        if self.config.functions is not None:
            args["functions"] = self.config.functions

        # Use the ** unpacking syntax to pass the arguments to the function
        response = openai.ChatCompletion.create(**args)

        return response.choices[0].message["content"]
