"""A module for managing local vLLM models."""

import logging
from dataclasses import dataclass
from typing import Optional

from sciphi.core import LLMProviderName
from sciphi.llm.base import LLM, GenerationConfig, LLMConfig
from sciphi.llm.config_manager import model_config

logging.basicConfig(level=logging.INFO)
from enum import Enum


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
    server_base: Optional[str] = None
    api_key: Optional[str] = None


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
            from sciphi.llm.models.openai_llm import OpenAILLM, OpenAIConfig

            self.model = OpenAILLM(OpenAIConfig(config.provider_name))
        else:
            raise NotImplementedError("Local vLLM models not yet implemented.")

    def get_chat_completion(
        self,
        messages: list[dict[str, str]],
        generation_config: GenerationConfig,
    ) -> str:
        """Get a completion from the SciPhi API based on the provided messages."""
        raise NotImplementedError(
            "Chat completion not yet implemented for SciPhi."
        )

    def get_instruct_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get an instruction completion from local SciPhi API."""
        import openai

        if self.config.server_base:
            openai.api_base = self.config.server_base
            openai.api_key = self.config.api_key
            return self.model.get_instruct_completion(
                prompt, generation_config
            )
        raise NotImplementedError("Missing server base.")

    def get_batch_instruct_completion(
        self, prompts: list[str], generation_config: GenerationConfig
    ) -> list[str]:
        """Get batch instruction completion from local vLLM."""
        raise NotImplementedError(
            "Batch instruction completion not yet implemented for SciPhi."
        )
