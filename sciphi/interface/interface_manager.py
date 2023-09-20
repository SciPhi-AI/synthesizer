"""A module for managing provider interfaces."""
import logging
from typing import Type

from sciphi.interface.base import LLMInterface, ProviderConfig, ProviderName
from sciphi.llm import LLMConfig, ModelName

logger = logging.getLogger(__name__)


class InterfaceManager:
    """A class to manage provider interfaces."""

    provider_registry: dict[ProviderName, ProviderConfig] = {}

    @staticmethod
    def register_provider(
        provider: Type[LLMInterface],
    ) -> Type[LLMInterface]:
        """Register a provider with the InterfaceManager."""
        InterfaceManager.provider_registry[
            provider.provider_name
        ] = ProviderConfig(
            provider.provider_name, provider.supported_models, provider
        )
        return provider

    @staticmethod
    def get_provider(
        provider_name: ProviderName,
        model_name: str,
        config: LLMConfig,
        *args,
        **kwargs,
    ) -> LLMInterface:
        """Gets an interface based on the given provider and model name."""

        logger.debug(
            f"Loaded the following provider registry: {InterfaceManager.provider_registry}"
        )
        provider = InterfaceManager.provider_registry.get(provider_name)

        if not provider:
            raise ValueError(f"Provider '{provider_name}' not supported.")

        if provider.models and ModelName(model_name) not in provider.models:
            raise ValueError(
                f"Model '{model_name}' not supported by provider '{provider_name}'."
            )

        logger.info(
            f"Using provider '{provider_name}' with model '{model_name}' and configuration '{config}'."
        )
        return provider.llm_class(config, *args, **kwargs)


llm_provider = InterfaceManager.register_provider
