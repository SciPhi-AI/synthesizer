"""A module for creating OpenAI model abstractions."""

from dataclasses import dataclass

import tiktoken

from sciphi.core import LLMProviderName
from sciphi.llm.base import LLM, GenerationConfig, LLMConfig
from sciphi.llm.config_manager import model_config


@model_config
@dataclass
class OpenAIConfig(LLMConfig):
    """Configuration for OpenAI models."""

    # Base
    provider_name: LLMProviderName = LLMProviderName.OPENAI


class OpenAILLM(LLM):
    """A concrete class for creating OpenAI models."""

    PROMPT_MEASUREMENT_PREFIX = (
        "<DUMMY PADDING, LOOKUP ACTUAL STRUCTUER LATER>"
    )

    def __init__(
        self,
        config: OpenAIConfig,
        *args,
        **kwargs,
    ) -> None:
        super().__init__()
        self.config: OpenAIConfig = config

        try:
            import openai
        except ImportError:
            raise ImportError(
                "Please install the openai package before attempting to run with an OpenAI model. This can be accomplished via `poetry install -E openai_support, ...OTHER_DEPENDENCIES_HERE`."
            )
        if not openai.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )
        # set the config here, again, for typing purposes
        if not isinstance(self.config, OpenAIConfig):
            raise ValueError(
                "The provided config must be an instance of OpenAIConfig."
            )

    def get_chat_completion(
        self,
        messages: list[dict[str, str]],
        generation_config: GenerationConfig,
    ) -> str:
        """Get a completion from the OpenAI API based on the provided messages."""
        import openai

        # Create a dictionary with the default arguments
        args = self._get_base_args(
            generation_config,
            OpenAILLM.PROMPT_MEASUREMENT_PREFIX
            + f"{OpenAILLM.PROMPT_MEASUREMENT_PREFIX}\n\n".join(
                [m["content"] for m in messages]
            ),
        )

        args["messages"] = messages

        # Conditionally add the 'functions' argument if it's not None
        if generation_config.functions is not None:
            args["functions"] = generation_config.functions

        # Create the chat completion
        response = openai.ChatCompletion.create(**args)
        return response.choices[0].message["content"]

    def get_instruct_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get an instruction completion from the OpenAI API based on the provided prompt."""
        import openai

        args = self._get_base_args(generation_config, prompt)

        args["prompt"] = prompt

        # Create the instruction completion
        response = openai.Completion.create(**args)
        return response.choices[0].text

    def _get_base_args(
        self,
        generation_config: GenerationConfig,
        prompt=None,
    ) -> dict:
        """Get the base arguments for the OpenAI API."""
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        args = {
            "model": generation_config.model_name,
            "temperature": generation_config.temperature,
            "top_p": generation_config.top_p,
            "max_tokens": generation_config.max_tokens_to_sample
            - len(encoding.encode(prompt)),
            "stream": generation_config.do_stream,
        }

        # Check if were using OpenAI api with re-routed base
        if self.config.provider_name in [
            LLMProviderName.VLLM,
            LLMProviderName.SCIPHI,
        ]:
            args["top_k"] = generation_config.top_k
            args["skip_special_tokens"] = generation_config.skip_special_tokens
            args["stop"] = generation_config.stop_token

        return args
