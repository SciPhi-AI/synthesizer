"""A module for managing provider interfaces."""
import logging
from typing import Type

from sciphi.interface.base import (
    InterfaceManager,
    RAGInterface,
    RAGProviderConfig,
    RAGProviderName,
)

logger = logging.getLogger(__name__)


class RAGInterfaceManager(InterfaceManager):
    """A class to manage provider interfaces."""

    provider_registry: dict[RAGProviderName, Type[RAGInterface]] = {}
    provider_config_registry: dict[
        RAGProviderName, Type[RAGProviderConfig]
    ] = {}

    @staticmethod
    def register_provider(
        provider: Type[RAGInterface],
    ) -> Type[RAGInterface]:
        """Register a provider with the RAGInterfaceManager."""
        RAGInterfaceManager.provider_registry[
            provider.provider_name
        ] = provider
        return provider

    @staticmethod
    def register_provider_config(
        config: Type[RAGProviderConfig],
    ) -> Type[RAGProviderConfig]:
        """Register a provider with the RAGInterfaceManager."""
        RAGInterfaceManager.provider_config_registry[
            config.provider_name
        ] = config
        return config

    @staticmethod
    def get_interface(
        provider_name: RAGProviderName,
        config: RAGProviderConfig,
        *args,
        **kwargs,
    ) -> RAGInterface:
        """Gets an interface based on  the given provider and model name."""

        logger.debug(
            f"Loaded the following provider registry: {RAGInterfaceManager.provider_registry}"
        )
        provider = RAGInterfaceManager.provider_registry.get(provider_name)

        if not provider:
            raise ValueError(f"Provider '{provider_name}' not supported.")

        logger.info(
            f"Using provider '{provider_name}' and configuration '{config}'."
        )
        return provider(config)

    @staticmethod
    def get_interface_from_args(
        provider_name: RAGProviderName,
        *args,
        **kwargs,
    ) -> RAGInterface:
        """Gets an interface based on the given provider and model name."""

        config = RAGInterfaceManager.provider_config_registry[provider_name](
            provider_name=provider_name, *args, **kwargs
        )

        return RAGInterfaceManager.get_interface(
            provider_name=provider_name,
            config=config,
            *args,
            **kwargs,
        )


rag_provider = RAGInterfaceManager.register_provider
rag_config = RAGInterfaceManager.register_provider_config
