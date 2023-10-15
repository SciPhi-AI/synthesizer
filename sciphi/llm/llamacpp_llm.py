"""A module for managing local Llama-cpp models."""

import logging
import time
from dataclasses import dataclass
from typing import Optional

from sciphi.core import ProviderName
from sciphi.llm.base import LLM, LLMConfig
from sciphi.llm.config_manager import model_config

logging.basicConfig(level=logging.INFO)

from multiprocessing import Lock, Value

# Create a multiprocessing-safe value for the counter and a lock
global_lock = Lock()
global_token_counter = Value("i", 0)
global_time_counter = Value("d", 0)


@model_config
@dataclass
class LLamaCPPConfig(LLMConfig):
    """Configuration for local LlamaCPP models."""

    # Base
    provider_name: ProviderName = ProviderName.LLAMACPP
    model_name: str = "./sciphi/models/dolphin-2.1-mistral-7b.Q6_K.gguf"
    temperature: float = 0.7
    top_p: float = 1.0
    # Port to use for local LlamaCPP API
    port: Optional[int] = None

    # Generation parameters
    top_k: int = 100
    max_tokens_to_sample: int = 256


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
                n_gpu_layers=8,
                n_ctx=8192,
                f16_kv=True,
            )
        else:
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "You specified a configuration port. Please install openai before attempting to run llamaCPP through a server. This can be accomplished via `poetry install -E openai,  ...OTHER_DEPENDENCIES_HERE`."
                )
        super().__init__(config)

    def get_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Get a completion from the OpenAI API based on the provided messages."""
        raise NotImplementedError(
            "Chat completion not yet implemented for LlamaCPP."
        )

    def get_instruct_completion(self, prompt: str) -> str:
        """Get an instruction completion from local LlamaCPP API."""
        if not self.config.port:
            return self.model(prompt, max_tokens=2000)["choices"][0]["text"]

        else:
            import openai

            openai.api_key = LlamaCPP.DUMMY_API_KEY
            openai.api_base = LlamaCPP.DUMMY_API_BASE.format(
                PORT=self.config.port
            )
            outputs = openai.Completion.create(
                model=self.config.model_name,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                max_tokens=self.config.max_tokens_to_sample,
                prompt=prompt,
            )

            return outputs["choices"][0]["text"]

    def get_batch_instruct_completion(self, prompts: list[str]) -> list[str]:
        """Get batch instruction completion from local LlamaCPP."""
        if self.config.port:
            return [
                self.model(prompt)["choices"][0]["text"] for prompt in prompts
            ]

        return [ele["choices"][0]["text"] for ele in self.model(prompts)]
