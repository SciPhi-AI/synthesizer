"""A module which defines interface abstractions for various LLM providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Type

from sciphi.core import ProviderName
from sciphi.llm import LLM, LLMConfig, ModelName


class LLMInterface(ABC):
    """An abstract class to provide a common interface for LLM providers."""

    provider_name: ProviderName
    supported_models: list[ModelName] = []

    def __init__(
        self,
        config: LLMConfig,
    ) -> None:
        self.config = config

    @property
    @abstractmethod
    def model(self) -> LLM:
        """Property to get the instance of LLM."""
        pass

    @abstractmethod
    def get_completion(self, prompt: str) -> str:
        """Abstract method to get a completion from the provider."""
        pass

    def get_batch_completion(self, prompts: List[str]) -> List[str]:
        """Get a batch of completions from the provider."""
        return [self.get_completion(prompt) for prompt in prompts]


@dataclass
class ProviderConfig:
    """A dataclass to hold the configuration for a provider."""

    provider_name: ProviderName
    models: List[ModelName]
    llm_class: Type[LLMInterface]
