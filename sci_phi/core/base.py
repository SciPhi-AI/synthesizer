"""Base classes and enums for zero-shot replication problems."""
from enum import Enum

OUTPUT_FILE_NAME = "{RUN_NAME}__model_eq_{MODEL}__temperature_eq_{TEMPERATURE}__version_eq_{VERSION}.jsonl"


class ProviderName(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGING_FACE = "hugging-face"
    VLLM = "vllm"
