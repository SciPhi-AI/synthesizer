"""A module for managing local vLLM models."""

import logging
import re
from dataclasses import dataclass
from typing import Optional

from sciphi.core import LLMProviderName
from sciphi.llm import LLM, GenerationConfig, LLMConfig
from sciphi.llm.config_manager import model_config

logging.basicConfig(level=logging.INFO)


@model_config
@dataclass
class SciPhiConfig(LLMConfig):
    """Configuration for local vLLM models."""

    # Base
    llm_provider_name: LLMProviderName = LLMProviderName.SCIPHI

    # SciPhi Extras...
    server_base: Optional[str] = None
    api_key: Optional[str] = None


class SciPhiLLM(LLM):
    """Configuration for local vLLM models."""

    def __init__(
        self,
        config: SciPhiConfig,
    ) -> None:
        self.config = config

    def get_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Get a completion from the SciPhi API based on the provided messages."""
        raise NotImplementedError(
            "Chat completion not yet implemented for SciPhi."
        )

    def get_instruct_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get an instruction completion from local SciPhi API."""
        import openai

        openai.api_base = self.config.server_base

        return openai.Completion.create(
            api_key=self.config.api_key,
            model=generation_config.model_name,
            temperature=generation_config.temperature,
            top_p=generation_config.top_p,
            top_k=generation_config.top_k,
            max_tokens=generation_config.max_tokens_to_sample,
            prompt=prompt,
            skip_special_tokens=False,
            stop=generation_config.stop_token,
        )

    def get_batch_instruct_completion(self, prompts: list[str]) -> list[str]:
        """Get batch instruction completion from local vLLM."""
        raise NotImplementedError(
            "Batch instruction completion not yet implemented for SciPhi."
        )
