import os
from dataclasses import dataclass

from agent_search.core import SERPClient

from synthesizer.core import RAGProviderName
from synthesizer.interface.base import RAGInterface, RAGProviderConfig
from synthesizer.interface.rag_interface_manager import (
    rag_config,
    rag_provider,
)


@dataclass
@rag_config
class AgentSearchRAGConfig(RAGProviderConfig):
    """An abstract class to hold the configuration for a RAG provider."""

    provider_name: RAGProviderName = RAGProviderName.AGENT_SEARCH
    api_base: str = "https://api.sciphi.ai"
    limit_broad_results: int = 1_000
    limit_deduped_url_results: int = 100
    limit_hierarchical_url_results: int = 25
    limit_final_pagerank_results: int = 10


@rag_provider
class AgentSearchRAGInterface(RAGInterface):
    """A RAG provider that uses Wikipedia as the retrieval source."""

    provider_name = RAGProviderName.AGENT_SEARCH
    FORMAT_INDENT = "        "

    def __init__(
        self,
        config: AgentSearchRAGConfig = AgentSearchRAGConfig(),
        *args,
        **kwargs,
    ) -> None:
        super().__init__(config)
        self.config: AgentSearchRAGConfig = config
        self.client = SERPClient(config.api_base)

    def get_rag_context(self, query) -> list[str]:
        """Get the context for a prompt."""
        api_key = self.config.api_key or os.getenv("SCIPHI_API_KEY")
        if not api_key:
            raise ValueError(
                "No API key provided. Please provide an API key or set the SCIPHI_API_KEY environment variable."
            )
        results = self.client.search(
            query,
            self.config.limit_broad_results,
            self.config.limit_deduped_url_results,
            self.config.limit_hierarchical_url_results,
            self.config.limit_final_pagerank_results,
        )
        return "\n".join(
            [
                f"{i+1}. URL: {result.url} (Score: {result.score:.2f})\nTitle:{result.title}\nSnippet:\n{result.text}"
                for i, result in enumerate(results)
            ]
        )
