"""A module which defines interface abstractions for various LLM providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Type

from sciphi.core import LLMProviderName, RAGProviderName
from sciphi.llm import LLM, LLMConfig, ModelName


@dataclass
class LLMProviderConfig:
    """A dataclass to hold the configuration for a provider."""

    llm_provider_name: LLMProviderName
    models: List[ModelName]
    llm_class: Type["LLMInterface"]


class LLMInterface(ABC):
    """An abstract class to provide a common interface for LLM providers."""

    llm_provider_name: LLMProviderName
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
class RAGProviderConfig(ABC):
    """An abstract class to hold the configuration for a RAG provider."""

    rag_provider_name: RAGProviderName
    base: str
    api_key: str
    max_context: int = 2_048


class RAGInterface(ABC):
    """An abstract class to provide a common interface for RAG providers."""

    rag_provider_name: RAGProviderName
    RAG_DISABLED_MESSAGE: str = "Not Available."

    def __init__(
        self,
        config: RAGProviderConfig,
    ) -> None:
        self.config = config

    @abstractmethod
    def get_contexts(self, prompts: list[str]) -> list[str]:
        """Get the context for a prompt."""
        pass


class InterfaceManager(ABC):
    """An abstract class to provide a common interface for interface managers."""

    provider_registry: dict[Any, Any] = {}

    @staticmethod
    @abstractmethod
    def register_provider(
        provider: Type[Any],
    ) -> Type[Any]:
        """Registers a provider with the interface manager."""
        pass

    @staticmethod
    @abstractmethod
    def get_interface(
        provider_name: Any,
        config: Any,
        *args,
        **kwargs,
    ) -> Any:
        """Gets an interface based on the given provider and model name."""
        pass

    @staticmethod
    @abstractmethod
    def get_interface_from_args(
        provider_name: Any,
        *args,
        **kwargs,
    ) -> Any:
        """Gets an interface based on the given provider and model name."""
        pass
