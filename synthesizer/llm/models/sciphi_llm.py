"""A module for creating SciPhi model abstractions."""
import os
from dataclasses import dataclass

from synthesizer.core import LLMProviderName
from synthesizer.llm.base import LLM, GenerationConfig, LLMConfig
from synthesizer.llm.config_manager import model_config


@model_config
@dataclass
class SciPhiConfig(LLMConfig):
    """Configuration for SciPhi models."""

    # Base
    provider_name: LLMProviderName = LLMProviderName.SCIPHI

    api_base: str = "https://api.sciphi.ai/v1"


class SciPhiLLM(LLM):
    """A concrete class for creating SciPhi models."""

    PROMPT_MEASUREMENT_PREFIX = (
        "<DUMMY PADDING, LOOKUP ACTUAL STRUCTUER LATER>"
    )

    def __init__(
        self,
        config: SciPhiConfig,
        *args,
        **kwargs,
    ) -> None:
        super().__init__()
        self.config: SciPhiConfig = config

        try:
            import openai
        except ImportError:
            raise ImportError(
                "Please install the synthesizer package before attempting to run with an SciPhi model. This can be accomplished via `pip install openai`."
            )

        sciphi_api_key = os.getenv("SCIPHI_API_KEY")
        openai.api_base = self.config.api_base
        if not sciphi_api_key:
            raise ValueError(
                "Please set the environment variable SCIPHI_API_KEY before attempting to run with the SciPhi provider."
            )
        openai.api_key = sciphi_api_key
        # set the config here, again, for typing purposes
        if not isinstance(self.config, SciPhiConfig):
            raise ValueError(
                "The provided config must be an instance of SciPhiConfig."
            )

    def get_chat_completion(
        self,
        messages: list[dict[str, str]],
        generation_config: GenerationConfig,
    ) -> str:
        """Get a completion from the SciPhi API based on the provided messages."""
        import openai

        # Create a dictionary with the default arguments
        args = self._get_base_args(
            generation_config,
            SciPhiLLM.PROMPT_MEASUREMENT_PREFIX
            + f"{SciPhiLLM.PROMPT_MEASUREMENT_PREFIX}\n\n".join(
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
        """Get an instruction completion from the SciPhi API based on the provided prompt."""
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
        """Get the base arguments for the SciPhi API."""

        args = {
            "model": generation_config.model_name,
            "temperature": generation_config.temperature,
            "top_p": generation_config.top_p,
            "stream": generation_config.do_stream,
            # TODO - We need to cap this to avoid potential errors when exceed max allowable context
            "max_tokens": generation_config.max_tokens_to_sample,
        }

        # Check if were using SciPhi api with re-routed base
        if self.config.provider_name in [
            LLMProviderName.VLLM,
            LLMProviderName.SCIPHI,
        ]:
            args["top_k"] = generation_config.top_k
            args["skip_special_tokens"] = generation_config.skip_special_tokens
            args["stop"] = generation_config.stop_token

        return args
