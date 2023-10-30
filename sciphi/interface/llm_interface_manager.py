"""A module for managing provider interfaces."""
import logging
from typing import Type

from sciphi.interface.base import (
    InterfaceManager,
    LLMInterface,
    LLMProviderConfig,
    LLMProviderName,
)
from sciphi.llm import LLMConfig, LLMConfigManager, ModelName

logger = logging.getLogger(__name__)


class LLMInterfaceManager(InterfaceManager):
    """A class to manage provider interfaces."""

    provider_registry: dict[LLMProviderName, LLMProviderConfig] = {}

    @staticmethod
    def register_provider(
        provider: Type[LLMInterface],
    ) -> Type[LLMInterface]:
        """Register a provider with the LLMInterfaceManager."""
        LLMInterfaceManager.provider_registry[
            provider.llm_provider_name
        ] = LLMProviderConfig(
            provider.llm_provider_name, provider.supported_models, provider
        )
        return provider

    @staticmethod
    def get_interface(
        provider_name: LLMProviderName,
        config: LLMConfig,
        *args,
        **kwargs,
    ) -> LLMInterface:
        """Gets an interface based on the given provider and model name."""
        logger.debug(
            f"Loaded the following provider registry: {LLMInterfaceManager.provider_registry}"
        )
        provider = LLMInterfaceManager.provider_registry.get(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not supported.")

        logger.info(
            f"Using provider '{provider_name}' with  and configuration '{config}'."
        )
        return provider.llm_class(config, **kwargs)

    @staticmethod
    def get_interface_from_args(
        provider_name: LLMProviderName,
        *args,
        **kwargs,
    ) -> LLMInterface:
        """Gets an interface based on the given provider and model name."""
        config = LLMConfigManager.get_config_for_provider(
            provider_name
        ).create(**kwargs)
        return LLMInterfaceManager.get_interface(
            provider_name=provider_name,
            config=config,
            **kwargs,
        )


llm_interface = LLMInterfaceManager.register_provider
