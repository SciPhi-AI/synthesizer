"""A module for base classes and enums for makers."""
from enum import Enum


class DataGeneratorMode(Enum):
    """What mode is the data maker in?"""

    SYNTHETIC = "synthetic"
    FROM_HF_DATASET = "from_hf_dataset"
