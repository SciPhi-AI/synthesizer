from abc import ABC, abstractmethod
from dataclasses import dataclass, field, InitVar
from enum import Enum
from typing import Any

from sci_phi.core import ProviderName


class ModelName(Enum):
    """An enum to hold the names of supported models."""

    # OpenAI Models

    ## GPT-3.5
    GPT_3p5_TURBO_0301 = "gpt-3.5-turbo-0301"
    GPT_3p5_TURBO_0613 = "gpt-3.5-turbo-0613"
    GPT_3p5_TURBO = "gpt-3.5-turbo"

    ## GPT-4
    GPT_4_0314 = "gpt-4-0314"
    GPT_4_0613 = "gpt-4-0613"
    GPT_4 = "gpt-4"

    # Anthropic Models

    CLAUDE_INSTANT_1 = "claude-instant-1"
    CLAUDE_2 = "claude-2"


from dataclasses import dataclass, field, fields


@dataclass
class LLMConfig(ABC):
    provider_name: ProviderName
    model_name: str
    version: str
    temperature: float
    top_p: float

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
    def get_completion(self, input: Any) -> str:
        """Abstract method to get a completion from the provider."""
        pass
