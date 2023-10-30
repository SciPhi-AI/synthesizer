"""A module for managing local vLLM models."""

import logging
from dataclasses import dataclass
from typing import Optional

from sciphi.core import LLMProviderName
from sciphi.llm import LLM, GenerationConfig, LLMConfig
from sciphi.llm.config_manager import model_config

logging.basicConfig(level=logging.INFO)
from enum import Enum


class SciPhiProviderMode(Enum):
    REMOTE = "remote"
    LOCAL_VLLM = "local-vllm"
    LOCAL_HF = "local-hf"


@model_config
@dataclass
class SciPhiConfig(LLMConfig):
    """Configuration for local vLLM models."""

    # Base
    provider_name: LLMProviderName = LLMProviderName.SCIPHI
    sub_provider_name: LLMProviderName = LLMProviderName.VLLM

    # SciPhi Extras...
    mode = SciPhiProviderMode.REMOTE
    server_base: Optional[str] = None
    api_key: Optional[str] = None


class SciPhiLLM(LLM):
    """Configuration for local vLLM models."""

    def __init__(
        self,
        config: SciPhiConfig,
        *args,
        **kwargs,
    ) -> None:
        print("config = ", config)
        self.config: SciPhiConfig = config
        if self.config.mode in [
            SciPhiProviderMode.REMOTE,
            SciPhiProviderMode.LOCAL_VLLM,
        ]:
            # Remtoe and local vLLM are both powered by vLLM
            assert self.config.sub_provider_name == LLMProviderName.VLLM
            from sciphi.llm.models.vllm_llm import (
                vLLMConfig,
                vLLMProviderMode,
                vLLM,
            )

            if self.config.mode == SciPhiProviderMode.REMOTE:
                self.model = vLLM(
                    vLLMConfig(
                        provider_name=config.provider_name,
                        server_base=config.server_base,
                        api_key=config.api_key,
                        mode=vLLMProviderMode.REMOTE,
                    ),
                )
        elif self.config.mode == SciPhiProviderMode.LOCAL_HF:
            from sciphi.llm.models import hugging_face_llm

        else:
            raise ValueError(f"Invalid mode: {self.config.mode}")

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
        return self.model.get_instruct_completion(prompt, generation_config)

    def get_batch_instruct_completion(
        self, prompts: list[str], generation_config: GenerationConfig
    ) -> list[str]:
        """Get batch instruction completion from local vLLM."""
        raise NotImplementedError(
            "Batch instruction completion not yet implemented for SciPhi."
        )
