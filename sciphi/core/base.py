"""Base classes and enums for zero-shot replication problems."""
from enum import Enum


class ProviderName(Enum):
    """Specifies the name of the LLM provider"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGING_FACE = "hugging-face"
    LLAMA_INDEX = "llama-index"
    VLLM = "vllm"
    LLAMACPP = "llamacpp"
