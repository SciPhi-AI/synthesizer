"""Base classes for language model providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from enum import Enum

from sciphi.core import ProviderName


class ModelName(Enum):
    """An enum to hold the names of supported models."""

    # OpenAI Models

    ## GPT-3.5
    GPT_3p5_TURBO_0301 = "gpt-3.5-turbo-0301"
    GPT_3p5_TURBO_0613 = "gpt-3.5-turbo-0613"
    GPT_3p5_TURBO = "gpt-3.5-turbo"
    GPT_3p5_TURBO_INSTRUCT = "gpt-3.5-turbo-instruct"

    ## GPT-4
    GPT_4_0314 = "gpt-4-0314"
    GPT_4_0613 = "gpt-4-0613"
    GPT_4 = "gpt-4"

    # Anthropic Models

    CLAUDE_INSTANT_1 = "claude-instant-1"
    CLAUDE_2 = "claude-2"


@dataclass
class LLMConfig(ABC):
    provider_name: ProviderName
    model_name: str
    temperature: float
    top_p: float

    version: str = "0.1.0"

    @classmethod
    def create(cls, **kwargs):
        valid_keys = {f.name for f in fields(cls)}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_keys}
        return cls(**filtered_kwargs)


class LLM(ABC):
    """An abstract class to provide a common interface for LLMs."""

    def __init__(
        self,
        config: LLMConfig,
    ) -> None:
        self.config = config

    @abstractmethod
    def get_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Abstract method to get a chat completion from the provider."""
        pass

    @abstractmethod
    def get_instruct_completion(self, instruction: str) -> str:
        """Abstract method to get an instruction completion from the provider."""
        pass
