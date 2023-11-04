from typing import Callable

from sciphi.core import RAGProviderName
from sciphi.interface.base import RAGInterface, RAGProviderConfig
from sciphi.interface.rag_interface_manager import rag_provider


@rag_provider
class LocalRAGInterface(RAGInterface):
    """A RAG provider that uses Wikipedia as the retrieval source."""

    provider_name = RAGProviderName.LOCAL
    FORMAT_INDENT = "        "

    def __init__(
        self,
        context_fn: Callable[[list[str]], list[str]],
        config: RAGProviderConfig = RAGProviderConfig(RAGProviderName.LOCAL),
        *args,
        **kwargs,
    ) -> None:
        super().__init__(config)
        self.config: RAGProviderConfig = config
        self.context_fn = context_fn

    def get_contexts(self, prompts: list[str]) -> list[str]:
        """Get the context for a prompt."""

        return self.context_fn(
            prompts,
        )
