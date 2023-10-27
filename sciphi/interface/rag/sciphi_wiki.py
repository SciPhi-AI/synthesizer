from dataclasses import dataclass
from textwrap import dedent

import requests

from sciphi.core import RAGProviderName
from sciphi.interface.base import RAGInterface, RAGProviderConfig
from sciphi.interface.rag_interface_manager import rag_config, rag_provider

""


@dataclass
@rag_config
class SciPhiWikiRAGConfig(RAGProviderConfig):
    """An abstract class to hold the configuration for a RAG provider."""

    rag_provider_name = RAGProviderName.SCIPHI_WIKI
    top_k: int = 10


@rag_provider
class SciPhiWikiRAGInterface(RAGInterface):
    """A RAG provider that uses Wikipedia as the retrieval source."""

    rag_provider_name = RAGProviderName.SCIPHI_WIKI
    FORMAT_INDENT = "        "

    def __init__(self, config: SciPhiWikiRAGConfig) -> None:
        super().__init__(config)
        self.config: SciPhiWikiRAGConfig = config

    def get_contexts(self, prompts: list[str]) -> list[str]:
        """Get the context for a prompt."""
        raw_contexts = wiki_search_api(
            prompts,
            self.config.base,
            self.config.token,
            self.config.top_k,
        )

        return [
            self._format_wiki_context(raw_context)
            for raw_context in raw_contexts
        ]

    def _format_wiki_context(self, context: str) -> str:
        """Format the context for a prompt."""
        truncated_context = context[0 : self.config.max_context]
        wiki_context = dedent(truncated_context)
        return "\n".join(
            [
                f"{SciPhiWikiRAGInterface.FORMAT_INDENT}{line}"
                for line in wiki_context.split("\n")
            ]
        )


def wiki_search_api(
    queries: list[str],
    rag_api_base: str,
    rag_api_key: str,
    top_k=10,
) -> dict:
    """
    Queries the search API with the provided credentials and query.
    The expected output is a JSON response containing the top_k examples.
    """
    # Make the GET request with basic authentication and the query parameter
    response = requests.get(
        rag_api_base,
        params={"queries": queries, "top_k": top_k},
        headers={"Authorization": f"Bearer {rag_api_key}"},
    )

    if response.status_code == 200:
        return response.json()  # Return the JSON response
    if "detail" in response.json():
        raise ValueError(
            f'Unexpected response from API - {response.json()["detail"]}'
        )
    else:
        raise ValueError(f"Unexpected response from API - {response.json()}")
