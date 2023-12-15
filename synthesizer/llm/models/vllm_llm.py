"""A module for managing local vLLM models."""
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from synthesizer.core import LLMProviderName
from synthesizer.llm.base import LLM, GenerationConfig, LLMConfig
from synthesizer.llm.config_manager import model_config

logging.basicConfig(level=logging.INFO)


class vLLMProviderMode(Enum):
    REMOTE = "remote"
    LOCAL = "local"


@model_config
@dataclass
class vLLMConfig(LLMConfig):
    """Configuration for local vLLM models."""

    # Base
    provider_name: LLMProviderName = LLMProviderName.VLLM

    # vLLM Extras...
    mode: vLLMProviderMode = vLLMProviderMode.REMOTE
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    # For local inference
    model_name: Optional[str] = None


class vLLM(LLM):
    """Configuration for local vLLM models."""

    def __init__(
        self,
        config: vLLMConfig,
        *args,
        **kwargs,
    ) -> None:
        self.config = config
        if config.mode == vLLMProviderMode.REMOTE:
            from synthesizer.llm.models.openai_llm import (
                OpenAIConfig,
                OpenAILLM,
            )

            self.openai_model = OpenAILLM(OpenAIConfig(config.provider_name))
        else:
            try:
                from vllm import LLM as vvLLM
            except ImportError:
                raise ImportError(
                    "Please install the vllm package before attempting to run with an vLLM model. This can be accomplished via `pip install vllm`."
                )

            self.vllm_model = vvLLM(model=config.model_name)

    def get_instruct_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get an instruction completion from local SciPhi API."""
        if self.config.mode == vLLMProviderMode.REMOTE:
            import openai

            if not self.config.api_base:
                raise ValueError(
                    "The api_base must be specified for remote vLLM models."
                )
            openai.api_base = self.config.api_base
            openai.api_key = self.config.api_key or os.getenv("VLLM_API_KEY")
            return self.openai_model.get_instruct_completion(
                prompt, generation_config
            )
        else:
            from vllm import SamplingParams

            self.sampling_params = SamplingParams(
                temperature=generation_config.temperature,
                top_p=generation_config.top_p,
                top_k=generation_config.top_k,
                max_tokens=generation_config.max_tokens_to_sample,
            )
            results = self.vllm_model.generate(
                prompt,
                sampling_params=self.sampling_params,
            )
            return results[0].outputs[0].text

    def get_batch_instruct_completion(
        self, prompts: list[str], generation_config: GenerationConfig
    ) -> list[str]:
        """Get batch instruction completion from the vLLM interface."""
        raise NotImplementedError(
            "Batch instruction completion not yet implemented for vLLM."
        )

    def get_chat_completion(
        self,
        messages: list[dict[str, str]],
        generation_config: GenerationConfig,
    ) -> str:
        """Get chat completion from the vLLM interface."""
        raise NotImplementedError(
            "Chat completion not yet implemented for vLLM."
        )
