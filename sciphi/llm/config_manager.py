"""A module to manage the configurations for models."""
from typing import Type

from sciphi.core import LLMProviderName
from sciphi.llm.base import LLMConfig


class LLMConfigManager:
    """A class to manage the configurations for models."""

    config_registry: dict[LLMProviderName, Type[LLMConfig]] = {}

    @staticmethod
    def get_config_for_provider(
        llm_provider_name: LLMProviderName,
    ) -> Type[LLMConfig]:
        """Get the configuration class for a given model."""
        config_class = LLMConfigManager.config_registry.get(llm_provider_name)

        if not config_class:
            raise ValueError(
                f"No provider configuration found for provider '{llm_provider_name}'."
            )

        return config_class

    @staticmethod
    def register_config(
        config_cls: Type[LLMConfig],
    ) -> Type[LLMConfig]:
        """Register a provider with the LLMConfigManager."""
        LLMConfigManager.config_registry[
            config_cls.llm_provider_name
        ] = config_cls
        return config_cls


model_config = LLMConfigManager.register_config
