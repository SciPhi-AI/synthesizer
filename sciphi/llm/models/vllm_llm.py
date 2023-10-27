"""A module for managing local vLLM models."""

import logging
import os
from dataclasses import dataclass
from typing import Optional

from sciphi.core import LLMProviderName
from sciphi.core.utils import time_function
from sciphi.llm.base import LLM, LLMConfig
from sciphi.llm.config_manager import model_config

logging.basicConfig(level=logging.INFO)


class TokenCounterUtility:
    """Class for tracking tokens per second."""

    def __init__(self) -> None:
        self.total_tokens = 0
        self.total_time = 0.0

    def update_counters(self, new_tokens: int, elapsed_time: int) -> None:
        self.total_tokens += new_tokens
        self.total_time += elapsed_time

    def get_tokens_per_second(
        self, new_tokens: int, elapsed_time: int
    ) -> float:
        return new_tokens / elapsed_time

    def get_avg_tokens_per_second(self):
        return (
            self.total_tokens / self.total_time if self.total_time > 0 else 0
        )


@model_config
@dataclass
class vLLMConfig(LLMConfig):
    """Configuration for local vLLM models."""

    # Base
    llm_provider_name: LLMProviderName = LLMProviderName.VLLM
    model_name: str = "gpt2"
    temperature: float = 0.7
    top_p: float = 1.0

    # Port to use for local vLLM API
    server_base: Optional[str] = None

    # Generation parameters
    top_k: int = 100
    max_tokens_to_sample: int = 256


class vLLM(LLM):
    """Configuration for local vLLM models."""

    def __init__(
        self,
        config: vLLMConfig,
    ) -> None:
        if config.server_base is None:
            try:
                from vllm import LLM as vvLLM
                from vllm import SamplingParams
            except ImportError:
                raise ImportError(
                    "Please install the vllm package before attempting to run with an vLLM model. This can be accomplished via `poetry install -E vllm_support, ...OTHER_DEPENDENCIES_HERE`."
                )
            self.model = vvLLM(model=config.model_name)
            self.sampling_params = SamplingParams(
                temperature=config.temperature,
                top_p=config.top_p,
                top_k=config.top_k,
                max_tokens=config.max_tokens_to_sample,
            )
            self.token_counter = TokenCounterUtility()
        else:
            try:
                import openai  # noqa: F401

                vllm_api_key = os.environ.get("VLLM_API_KEY")
                if not vllm_api_key:
                    raise ValueError(
                        "`VLLM_API_KEY` environment variable must be set when specifying `server_base` on a vLLM config."
                    )
                openai.api_key = vllm_api_key
            except ImportError:
                raise ImportError(
                    "You specified a vLLM server_base. Please install openai before attempting to run vLLM through a server. This can be accomplished via `poetry install -E openai,  ...OTHER_DEPENDENCIES_HERE`."
                )
        super().__init__(config)
        self.config: vLLMConfig = config

    def get_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Get a completion from the vLLM API based on the provided messages."""
        raise NotImplementedError(
            "Chat completion not yet implemented for vLLM."
        )

    def get_instruct_completion(self, prompt: str) -> str:
        """Get an instruction completion from local vLLM API."""
        if self.config.server_base:
            import openai

            openai.api_base = self.config.server_base
            outputs = openai.Completion.create(
                model=self.config.model_name,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                max_tokens=self.config.max_tokens_to_sample,
                prompt=prompt,
            )

            return outputs["choices"][0]["text"]
        else:
            results, elapsed_time = self._timed_generate([prompt])
            total_tokens = len(results[0].token_ids)
            self.token_counter.update_counters(
                results[0].token_ids, elapsed_time
            )

            tokens_per_second = self.token_counter.get_tokens_per_second(
                total_tokens, elapsed_time
            )
            avg_tokens_per_second = (
                self.token_counter.get_avg_tokens_per_second()
            )

            print(
                f"Latest batch - Completion tokens per second: {tokens_per_second}"
            )
            print(
                f"Running average - Completion tokens per second: {avg_tokens_per_second}"
            )
            return results[0].outputs[0].text

    def get_batch_instruct_completion(self, prompts: list[str]) -> list[str]:
        """Get batch instruction completion from local vLLM."""
        if self.config.server_base:
            # TODO - Consider async implementation for batching
            return [self.get_instruct_completion(prompt) for prompt in prompts]

        results, elapsed_time = self._timed_generate(prompts)
        total_tokens = sum(len(ele.outputs[0].token_ids) for ele in results)
        self.token_counter.update_counters(total_tokens, elapsed_time)

        tokens_per_second = self.token_counter.get_tokens_per_second(
            total_tokens, elapsed_time
        )
        avg_tokens_per_second = self.token_counter.get_avg_tokens_per_second()

        print(f"Latest batch - Tokens per second: {tokens_per_second}")
        print(f"Running average - Tokens per second: {avg_tokens_per_second}")

        return [ele.outputs[0].text for ele in results]

    @time_function
    def _timed_generate(self, prompts):
        return self.model.generate(prompts, self.sampling_params)
