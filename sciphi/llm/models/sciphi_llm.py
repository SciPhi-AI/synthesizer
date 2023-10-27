"""A module for managing local vLLM models."""

import logging
from dataclasses import dataclass
from typing import Optional

from sciphi.core import LLMProviderName, RAGProviderName
from sciphi.interface.rag_interface_manager import RAGInterfaceManager
from sciphi.llm.config_manager import model_config
from sciphi.llm.models.vllm_llm import vLLM, vLLMConfig

logging.basicConfig(level=logging.INFO)


class SciPhiFormatter:
    """Formatter for SciPhi."""

    INSTRUCTION_PREFIX = "### Instruction:\n"
    INSTRUCTION_SUFFIX = "### Response:\n"
    INIT_PARAGRAPH_TOKEN = "<paragraph>"
    END_PARAGRAPH_TOKEN = "</paragraph>"

    RETRIEVAL_TOKEN = "[Retrieval]"
    NO_RETRIEVAL_TOKEN = "[No Retrieval]"
    EVIDENCE_TOKEN = "[Continue to Use Evidence]"
    RELEVANT_TOKEN = "[Relevant]"
    PARTIALLY_SUPPORTED_TOKEN = "[Partially supported]"
    SUFFIX_CRUFT = "[Utility:5]</s>"

    @staticmethod
    def format_prompt(input: str) -> str:
        """Format the prompt for the model."""
        return f"{SciPhiFormatter.INSTRUCTION_PREFIX}\n{input}\n\n{SciPhiFormatter.INSTRUCTION_SUFFIX}"

    @staticmethod
    def remove_cruft(result: str) -> str:
        return (
            result.replace(SciPhiFormatter.RETRIEVAL_TOKEN, " ")
            .replace(SciPhiFormatter.NO_RETRIEVAL_TOKEN, "")
            .replace(SciPhiFormatter.EVIDENCE_TOKEN, " ")
            .replace(SciPhiFormatter.SUFFIX_CRUFT, "")
            .replace(SciPhiFormatter.RELEVANT_TOKEN, "")
            .replace(SciPhiFormatter.PARTIALLY_SUPPORTED_TOKEN, "")
        )


@model_config
@dataclass
class SciPhiConfig(vLLMConfig):
    """Configuration for local vLLM models."""

    # Base
    provider_name: LLMProviderName = LLMProviderName.SCIPHI
    model_name: str = "selfrag/selfrag_llama2_7b"
    temperature: float = 0.1
    top_p: float = 1.0
    top_k: int = 100
    max_tokens_to_sample: int = 256
    server_base: Optional[str] = None

    # RAG Parameters
    rag_provider_name: RAGProviderName = RAGProviderName.SCIPHI_WIKI
    rag_provider_base: Optional[str] = None
    rag_provider_token: Optional[str] = None
    rag_top_k: int = 100


class SciPhiLLM(vLLM):
    """Configuration for local vLLM models."""

    def __init__(
        self,
        config: SciPhiConfig,
    ) -> None:
        super().__init__(config)
        from vllm import SamplingParams

        self.config: SciPhiConfig = config
        self.sampling_params = SamplingParams(
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k,
            max_tokens=config.max_tokens_to_sample,
            skip_special_tokens=False,  # RAG Fine Tune includes special tokens
            stop=SciPhiFormatter.INIT_PARAGRAPH_TOKEN,  # Stops on Retrieval
        )

        self.rag_provider = RAGInterfaceManager.get_interface_from_args(
            provider_name=config.rag_provider_name,
            base=config.rag_provider_base or "http://localhost:8000",
            token=config.rag_provider_token or "",
            top_k=config.rag_top_k,
        )

    def get_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Get a completion from the SciPhi API based on the provided messages."""
        raise NotImplementedError(
            "Chat completion not yet implemented for SciPhi."
        )

    def get_instruct_completion(self, prompt: str) -> str:
        """Get an instruction completion from local SciPhi API."""
        import openai

        openai.api_base = self.config.server_base or ""
        return openai.Completion.create(
            model=self.config.model_name,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            max_tokens=self.config.max_tokens_to_sample,
            prompt=prompt,
            skip_special_tokens=False,
            stop=SciPhiFormatter.INIT_PARAGRAPH_TOKEN,
        )

    def get_batch_instruct_completion(self, prompts: list[str]) -> list[str]:
        """Get batch instruction completion from local vLLM."""
        raise NotImplementedError(
            "Batch instruction completion not yet implemented for SciPhi."
        )
