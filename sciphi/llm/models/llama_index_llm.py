"""A module for creating LlamaIndex models."""
import os
from dataclasses import dataclass

from sciphi.core import LLMProviderName
from sciphi.core.utils import get_data_dir
from sciphi.llm.base import LLM
from sciphi.llm.config_manager import model_config
from sciphi.llm.models.openai_llm import OpenAIConfig


@model_config
@dataclass
class LLamaIndexConfig(OpenAIConfig):
    """A class to manage the configurations for LlamaIndex."""

    llm_provider_name: "LLMProviderName" = LLMProviderName.LLAMA_INDEX

    # LlamaIndex-specific configs
    # Defaults to the library of phi textbook
    llama_data_dir: str = os.path.join(
        get_data_dir(), "library_of_phi", "Aerodynamics_of_Viscous_Fluids.md"
    )
    llama_index_name: str = "vector_index"
    llama_out_store: str = "storage"
    llama_load_from_avail_store: bool = True
    llama_chunk_size: int = 512
    llama_top_k_similarity: int = 5


class LlamaIndexLLM(LLM):
    """A concrete class for creating LlamaIndex models."""

    def __init__(
        self,
        config: LLamaIndexConfig,
    ) -> None:
        super().__init__(config)
        try:
            import openai
            from llama_index import (
                OpenAIEmbedding,
                ServiceContext,
                SimpleDirectoryReader,
                StorageContext,
                VectorStoreIndex,
                load_index_from_storage,
            )
            from llama_index.llms import OpenAI
        except ImportError:
            raise ImportError(
                "Please install the llama_index package before attempting to run with a LlamaIndex. This can be accomplished via `poetry install -E llama_index_support, ...OTHER_DEPENDENCIES_HERE`."
            )
        if not openai.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )
        self.config: LLamaIndexConfig = config

        llama_index_llm = OpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens_to_sample,
        )
        embed_model = OpenAIEmbedding()

        service_context = ServiceContext.from_defaults(
            llm=llama_index_llm,
            embed_model=embed_model,
        )

        store_dir = os.path.join(
            self.config.llama_data_dir, self.config.llama_out_store
        )
        store_dir_exists = os.path.exists(store_dir)
        loaded_store = False
        if not self.config.llama_load_from_avail_store or not store_dir_exists:
            # Creating a new store
            # Load Documents
            documents = SimpleDirectoryReader(
                self.config.llama_data_dir
            ).load_data()

            # Create index with specified chunk size
            index = VectorStoreIndex.from_documents(
                documents, chunk_size=self.config.llama_chunk_size
            )
        else:
            # Loading from an existing store
            storage_context = StorageContext.from_defaults(
                persist_dir=store_dir
            )

            index: VectorStoreIndex = load_index_from_storage(  # type: ignore
                storage_context, index_id=self.config.llama_index_name
            )
            loaded_store = True

        # Create a query engine with the retriever and response synthesizer
        self.query_engine = index.as_query_engine(
            similarity_top_k=self.config.llama_top_k_similarity,
            service_context=service_context,
        )
        # Save index to disk if it was just created
        # TODO - Add some upstream customization around this.
        if not loaded_store:
            index.set_index_id(self.config.llama_index_name)
            index.storage_context.persist(store_dir)

    def get_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Get a completion from the LlamaIndex API based on the provided messages."""
        raise NotImplementedError(
            "Chat completion is not yet supported for LlamaIndex."
        )

    def get_instruct_completion(self, instruction: str) -> str:
        """Get an instruction completion from the LlamaIndex API based on the provided prompt."""
        # Clean the typical instruction completion for better search results
        if "### Instruction:" in instruction:
            instruction = instruction.split("### Instruction:")[1].strip()
        if "### Response:" in instruction:
            instruction = instruction.replace("### Response:", "").strip()
        return self.query_engine.query(instruction).response  # type: ignore
