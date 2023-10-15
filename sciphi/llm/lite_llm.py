"""A module for creating OpenAI model abstractions."""

from dataclasses import dataclass
from typing import Optional

import tiktoken

from sciphi.core import ProviderName
from sciphi.llm.base import LLM, LLMConfig
from sciphi.llm.config_manager import model_config


@model_config
@dataclass
class LiteLLMConfig(LLMConfig):
    """Configuration for LiteLLM models."""

    # Base
    provider_name: ProviderName = ProviderName.OPENAI
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    top_p: float = 1.0

    # OpenAI Extras
    do_stream: bool = False
    max_tokens_to_sample: int = 256
    max_total_tokens = 4_096  # TODO - automate population of this.
    functions: Optional[list[dict]] = None


class LiteLLM(LLM):
    """A concrete class for creating LiteLLM models."""

    def __init__(
        self,
        config: LiteLLMConfig,
    ) -> None:
        super().__init__(config)
        try:
            import litellm  # noqa: F401
        except ImportError:
            raise ImportError(
                "Please install the litellm package before attempting to run with a LiteLLM model. This can be accomplished via `poetry add litellm`."
            )
        # set the config here, again, for typing purposes
        if not isinstance(self.config, LiteLLMConfig):
            raise ValueError(
                "The provided config must be an instance of LiteLLMConfig."
            )
        self.config: LiteLLMConfig = config

    def get_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Get a completion from the LiteLLM API based on the provided messages."""
        import litellm

        # Create a dictionary with the default arguments
        args = self._get_base_args()

        args["messages"] = messages

        # Conditionally add the 'functions' argument if it's not None
        if self.config.functions is not None:
            args["functions"] = self.config.functions

        # Create the chat completion
        response = litellm.completion(**args)
        return response.choices[0].message["content"]

    def get_instruct_completion(self, instruction: str) -> str:
        """Get an instruction completion from the LiteLLM based on the provided prompt."""
        import litellm

        # Create a dictionary with the default arguments
        args = self._get_base_args(instruction)

        # Create the instruction completion
        args["prompt"] = instruction
        response = litellm.completion(**args)
        return response.choices[0].text

    def _get_base_args(
        self,
        prompt=None,
    ) -> dict:
        """Get the base arguments for the OpenAI API."""
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

        return {
            "model": self.config.model_name,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_tokens": self.config.max_total_tokens
            - len(encoding.encode(prompt))
            if prompt
            else self.config.max_tokens_to_sample,
            "stream": self.config.do_stream,
        }
