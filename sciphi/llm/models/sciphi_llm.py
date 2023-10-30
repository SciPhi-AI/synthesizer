"""A module for managing local vLLM models."""

import logging
import re
from dataclasses import dataclass
from typing import Optional

from sciphi.core import LLMProviderName, RAGProviderName
from sciphi.llm.base import LLM, LLMConfig
from sciphi.llm.config_manager import model_config

logging.basicConfig(level=logging.INFO)


class SciPhiFormatter:
    """Formatter for SciPhi."""

    INSTRUCTION_PREFIX = "### Instruction:\n"
    INSTRUCTION_SUFFIX = "### Response:\n"
    INIT_PARAGRAPH_TOKEN = "<paragraph>"
    END_PARAGRAPH_TOKEN = "</paragraph>"

    RETRIEVAL_TOKEN = "[Retrieval]"
    FULLY_SUPPORTED = "[Fully supported]"
    NO_RETRIEVAL_TOKEN = "[No Retrieval]"
    EVIDENCE_TOKEN = "[Continue to Use Evidence]"
    UTILITY_TOKEN = "[Utility:5]"
    RELEVANT_TOKEN = "[Relevant]"
    PARTIALLY_SUPPORTED_TOKEN = "[Partially supported]"
    NO_SUPPORT_TOKEN = "[No support / Contradictory]"
    END_TOKEN = "</s>"

    @staticmethod
    def format_prompt(input: str) -> str:
        """Format the prompt for the model."""
        return f"{SciPhiFormatter.INSTRUCTION_PREFIX}\n{input}\n\n{SciPhiFormatter.INSTRUCTION_SUFFIX}"

    @staticmethod
    def extract_post_prompt(completion: str) -> str:
        if SciPhiFormatter.INSTRUCTION_SUFFIX not in completion:
            raise ValueError(
                f"Full Completion does not contain {SciPhiFormatter.INSTRUCTION_SUFFIX}"
            )

        return completion.split(SciPhiFormatter.INSTRUCTION_SUFFIX)[1]

    @staticmethod
    def remove_cruft(result: str) -> str:
        pattern = f"{re.escape(SciPhiFormatter.INIT_PARAGRAPH_TOKEN)}.*?{re.escape(SciPhiFormatter.END_PARAGRAPH_TOKEN)}"
        # Remove <paragraph>{arbitrary text...}</paragraph>
        result = re.sub(pattern, "", result, flags=re.DOTALL)

        return (
            result.replace(SciPhiFormatter.RETRIEVAL_TOKEN, "")
            .replace(SciPhiFormatter.NO_RETRIEVAL_TOKEN, "")
            .replace(SciPhiFormatter.EVIDENCE_TOKEN, " ")
            .replace(SciPhiFormatter.UTILITY_TOKEN, "")
            .replace(SciPhiFormatter.RELEVANT_TOKEN, "")
            .replace(SciPhiFormatter.PARTIALLY_SUPPORTED_TOKEN, "")
            .replace(SciPhiFormatter.FULLY_SUPPORTED, "")
            .replace(SciPhiFormatter.END_TOKEN, "")
            .replace(SciPhiFormatter.NO_SUPPORT_TOKEN, "")
        )


@model_config
@dataclass
class SciPhiConfig(LLMConfig):
    """Configuration for local vLLM models."""

    # Base
    llm_provider_name: LLMProviderName = LLMProviderName.SCIPHI
    model_name: str = "SciPhi/SciPhi-Self-RAG-Mistral-7B-32k"
    temperature: float = 0.1
    top_p: float = 1.0
    top_k: int = 100

    # SciPhi Extras...
    max_tokens_to_sample: int = 1_024
    server_base: Optional[str] = None
    api_key: Optional[str] = None

    # RAG Parameters
    rag_provider_name: RAGProviderName = RAGProviderName.SCIPHI_WIKI
    rag_server_base: Optional[str] = None
    rag_api_key: Optional[str] = None
    rag_top_k: int = 100


class SciPhiLLM(LLM):
    """Configuration for local vLLM models."""

    def __init__(
        self,
        config: SciPhiConfig,
    ) -> None:
        super().__init__(config)
        # Hack to avoid typing errors
        self.config: SciPhiConfig = config

        from sciphi.interface.rag_interface_manager import RAGInterfaceManager

        self.rag_provider = RAGInterfaceManager.get_interface_from_args(
            provider_name=config.rag_provider_name,
            base=config.rag_server_base or config.server_base,
            api_key=config.rag_api_key or config.api_key,
            top_k=config.rag_top_k,
        )

    def get_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Get a completion from the SciPhi API based on the provided messages."""
        raise NotImplementedError(
            "Chat completion not yet implemented for SciPhi."
        )

    def _get_instruct_completion(self, prompt: str) -> str:
        """Get an instruction completion from local SciPhi API."""
        import openai

        openai.api_base = self.config.server_base or ""
        return openai.Completion.create(
            model=self.config.model_name,
            api_key=self.config.api_key,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            max_tokens=self.config.max_tokens_to_sample,
            prompt=prompt,
            skip_special_tokens=False,
            stop=SciPhiFormatter.INIT_PARAGRAPH_TOKEN,
        )

    def get_instruct_completion(self, prompt: str) -> str:
        """Get an instruction completion from local SciPhi API."""
        completion = ""
        while True:
            prompt_with_context = (
                SciPhiFormatter.format_prompt(prompt) + completion
            )
            latest_completion = self._get_instruct_completion(
                prompt_with_context
            )["choices"][0]["text"].strip()
            completion += latest_completion

            if not completion.endswith(SciPhiFormatter.RETRIEVAL_TOKEN):
                break
            context_query = (
                prompt
                if completion == SciPhiFormatter.RETRIEVAL_TOKEN
                else f"{SciPhiFormatter.remove_cruft(completion)}"
            )
            context = self.rag_provider.get_contexts([context_query])[0]
            completion += f"{SciPhiFormatter.INIT_PARAGRAPH_TOKEN}{context}{SciPhiFormatter.END_PARAGRAPH_TOKEN}"
        return SciPhiFormatter.remove_cruft(completion)

    def get_batch_instruct_completion(self, prompts: list[str]) -> list[str]:
        """Get batch instruction completion from local vLLM."""
        raise NotImplementedError(
            "Batch instruction completion not yet implemented for SciPhi."
        )
