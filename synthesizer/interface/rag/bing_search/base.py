import os
from dataclasses import dataclass

from synthesizer.core import RAGProviderName
from synthesizer.interface.base import (
    RAGInterface,
    RAGProviderConfig,
    RagResult,
)
from synthesizer.interface.rag_interface_manager import (
    rag_config,
    rag_provider,
)

from .bing_client import BingSearchClient  # Import your BingSearchClient


@dataclass
@rag_config
class BingRAGConfig(RAGProviderConfig):
    """Configuration for the Bing RAG provider."""

    provider_name: RAGProviderName = RAGProviderName.BING
    api_base: str = "https://api.bing.microsoft.com/v7.0/search"
    limit_results: int = 30


@rag_provider
class BingRAGInterface(RAGInterface):
    """A RAG provider that uses Bing as the retrieval source."""

    provider_name = RAGProviderName.BING
    FORMAT_INDENT = "        "

    def __init__(
        self, config: BingRAGConfig = BingRAGConfig(), *args, **kwargs
    ) -> None:
        super().__init__(config)
        self.config: BingRAGConfig = config
        print('self.config = ', self.config)
        api_key = self.config.api_key or os.getenv("BING_API_KEY")
        if not api_key:
            raise ValueError(
                "No API key provided. Please provide an API key or set the BING_API_KEY environment variable."
            )
        self.client = BingSearchClient(api_key)

    def get_rag_context(self, query) -> RagResult:
        """Retrieve context for a given query using Bing."""
        results = self.client.search(query, self.config.limit_results)
        serp_results = self.client.format_as_serp_results(results)
        SPLIT_MARKER = "/"
        context = "\n\n".join(
            [
                f"{i+1}. URL: {SPLIT_MARKER.join(result.url.split(SPLIT_MARKER)[0:4])}\nTitle: {result.title}\nSnippet:\n{result.text}"
                for i, result in enumerate(serp_results)
            ]
        )
        return RagResult(
            context=context,
            meta_data=[ele.to_string_dict() for ele in serp_results],
        )
