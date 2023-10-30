"""A module for interfacing with local vLLM models"""
import logging
import re
from typing import List

from sciphi.interface.base import LLMInterface, LLMProviderName, RAGInterface
from sciphi.interface.llm_interface_manager import llm_interface
from sciphi.llm import GenerationConfig, SciPhiConfig, SciPhiLLM

logger = logging.getLogger(__name__)


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


@llm_interface
class SciPhiInterface(LLMInterface):
    """A class to interface with local vLLM models."""

    llm_provider_name = LLMProviderName.SCIPHI

    def __init__(
        self,
        config: SciPhiConfig,
        rag_interface: RAGInterface,
        *args,
        **kwargs,
    ) -> None:
        self._model = SciPhiLLM(config)
        self.rag_interface = rag_interface

    def get_completion(
        self, prompt: str, generation_config: GenerationConfig
    ) -> str:
        """Get a completion from the local vLLM provider."""

        logger.debug(
            f"Requesting completion from local vLLM with model={generation_config.model_name} and prompt={prompt}"
        )
        completion = ""
        while True:
            prompt_with_context = (
                SciPhiFormatter.format_prompt(prompt) + completion
            )
            latest_completion = self.model.get_instruct_completion(
                prompt_with_context, generation_config
            )["choices"][0]["text"].strip()
            completion += latest_completion

            if not completion.endswith(SciPhiFormatter.RETRIEVAL_TOKEN):
                break
            context_query = (
                prompt
                if completion == SciPhiFormatter.RETRIEVAL_TOKEN
                else f"{SciPhiFormatter.remove_cruft(completion)}"
            )
            context = self.rag_interface.get_contexts([context_query])[0]
            completion += f"{SciPhiFormatter.INIT_PARAGRAPH_TOKEN}{context}{SciPhiFormatter.END_PARAGRAPH_TOKEN}"
        return SciPhiFormatter.remove_cruft(completion)

    def get_batch_completion(
        self, prompts: List[str], generation_config: GenerationConfig
    ) -> List[str]:
        """Get a completion from the local vLLM provider."""

        logger.debug(
            f"Requesting completion from local vLLM with model={generation_config.model_name} and prompts={prompts}"
        )
        return self.model.get_batch_instruct_completion(
            prompts, generation_config
        )

    @property
    def model(self) -> SciPhiLLM:
        return self._model
