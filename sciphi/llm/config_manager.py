"""A module to manage the configurations for models."""
from typing import Type

from sciphi.core import ProviderName
from sciphi.llm.base import LLMConfig


class LLMConfigManager:
    """A class to manage the configurations for models."""

    config_registry: dict[ProviderName, Type[LLMConfig]] = {}

    @staticmethod
    def get_config_for_provider(
        provider_name: ProviderName,
    ) -> Type[LLMConfig]:
        """Get the configuration class for a given model."""

        config_class = LLMConfigManager.config_registry.get(provider_name)

        if not config_class:
            raise ValueError(
                f"No provider configuration found for provider '{provider_name}'."
            )

        return config_class

    @staticmethod
    def register_config(
        config_cls: Type[LLMConfig],
    ) -> Type[LLMConfig]:
        """Register a provider with the LLMConfigManager."""
        LLMConfigManager.config_registry[config_cls.provider_name] = config_cls
        return config_cls


model_config = LLMConfigManager.register_config
