"""Base classes and enums for zero-shot replication problems."""
from enum import Enum


class LLMProviderName(Enum):
    """Specifies the name of the LLM provider"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGING_FACE = "hugging-face"
    LLAMA_INDEX = "llama-index"
    VLLM = "vllm"
    LLAMACPP = "llamacpp"
    LITE_LLM = "lite-llm"
    SCIPHI = "sciphi"


class RAGProviderName(Enum):
    LOCAL = "local"
    AGENT_SEARCH = "agent-search"
    GOOGLE_SEARCH = "google-search"
