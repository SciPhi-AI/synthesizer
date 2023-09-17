"""Defines the abstract LLMInterface and related enums"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Type

from sci_phi.core import ProviderName
from sci_phi.llm import LLM, LLMConfig, ModelName


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


@dataclass
class ProviderConfig:
    """A dataclass to hold the configuration for a provider."""

    provider_name: ProviderName
    models: List[ModelName]
    llm_class: Type[LLMInterface]
