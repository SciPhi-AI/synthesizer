"""Base classes and enums for zero-shot replication problems."""
from enum import Enum


class ProviderName(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGING_FACE = "hugging-face"
    VLLM = "vllm"
