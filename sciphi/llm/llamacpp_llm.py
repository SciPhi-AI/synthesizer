"""A module for managing local Llama-cpp models."""

import logging
from dataclasses import dataclass

from sciphi.core import ProviderName
from sciphi.llm.base import LLM, LLMConfig
from sciphi.llm.config_manager import model_config

logging.basicConfig(level=logging.INFO)


@model_config
@dataclass
class LLamaCPPConfig(LLMConfig):
    """Configuration for local LlamaCPP models."""

    # Base
    provider_name: ProviderName = ProviderName.LLAMACPP
    model_name: str = "./sciphi/models/dolphin-2.1-mistral-7b.Q6_K.gguf"
    max_tokens_to_sample: int = 256
    n_gpu_layers: int = 8
    n_ctx: int = 8192
    f16_kv: bool = True


class LlamaCPP(LLM):
    """Configuration for local LlamaCPP models."""

    DUMMY_API_KEY = "EMPTY"
    DUMMY_API_BASE = "http://localhost:{PORT}/v1"

    def __init__(
        self,
        config: LLamaCPPConfig,
    ) -> None:
        if config.port is None:
            try:
                from llama_cpp import Llama
            except ImportError:
                raise ImportError(
                    "Please install the llama_cpp package before attempting to run with an LLamaCPP model. This can be accomplished via `poetry install -E llamacpp_support, ...OTHER_DEPENDENCIES_HERE`."
                )
            self.model = Llama(
                model_path=config.model_name,
                n_gpu_layers=config.n_gpu_layers,
                n_ctx=config.n_ctx,
                f16_kv=config.f16_kv,
            )
        super().__init__(config)

    def get_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Get a completion from the LlamaCPP model based on the provided messages."""
        raise NotImplementedError("Chat completion not yet implemented for LlamaCPP.")

    def get_instruct_completion(self, prompt: str) -> str:
        """Get an instruction completion from local LlamaCPP API."""
        return self.model(prompt, max_tokens=self.config.max_tokens_to_sample)["choices"][0][
            "text"
        ]

    def get_batch_instruct_completion(self, prompts: list[str]) -> list[str]:
        """Get batch instruction completion from local LlamaCPP."""
        return [ele["choices"][0]["text"] for ele in self.model(prompts)]
